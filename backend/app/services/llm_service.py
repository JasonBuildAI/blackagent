"""
LLM 服务

支持从数据库动态加载配置。
当 LLM 不可用时，所有方法返回 None，
调用方自动回退到基于规则的实现。
"""

import asyncio
import json
import logging
from typing import Optional, Any, Dict, List

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """LLM 服务封装，支持自动降级和动态配置"""

    def __init__(self):
        # 从环境变量读取初始配置
        self._env_api_key = settings.LLM_API_KEY
        self._env_api_base = settings.LLM_API_BASE
        self._env_model = settings.LLM_MODEL

        # 当前配置（可能被动态更新）
        self.enabled = settings.LLM_ENABLED
        self.api_base = self._env_api_base.rstrip("/")
        self.api_key = self._env_api_key
        self.model = self._env_model
        self.timeout = settings.LLM_TIMEOUT
        self.max_retries = settings.LLM_MAX_RETRIES
        self.retry_backoff = settings.LLM_RETRY_BACKOFF

        if self.enabled:
            logger.info(f"LLM服务已启用(环境变量): model={self.model}, base={self.api_base}")
        else:
            logger.info("LLM服务未启用(环境变量)，将使用基于规则的降级方案，或等待前端配置")

    async def reload_config_from_db(self, db) -> bool:
        """从数据库重新加载配置"""
        try:
            from app.services.settings_service import settings_service
            config = await settings_service.get_llm_config(db)

            self.api_key = config["api_key"] or self._env_api_key
            self.api_base = config["api_base"].rstrip("/") or self._env_api_base.rstrip("/")
            self.model = config["model"] or self._env_model
            self.enabled = bool(self.api_key and self.api_key.strip())

            if self.enabled:
                logger.info(f"LLM配置已更新(数据库): model={self.model}")
            return True
        except Exception as e:
            logger.error(f"从数据库加载LLM配置失败: {e}")
            return False

    def _build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_url(self, endpoint: str) -> str:
        return f"{self.api_base}/{endpoint.lstrip('/')}"

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> Optional[str]:
        """
        调用 LLM chat completion

        Args:
            messages: 消息列表 [{"role": "system/user/assistant", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大输出 token 数

        Returns:
            LLM 返回的文本内容，失败时返回 None
        """
        if not self.enabled:
            return None

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        last_error = None
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        self._build_url("chat/completions"),
                        headers=self._build_headers(),
                        json=payload,
                    )
                    response.raise_for_status()
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return content.strip() if content else None

            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(
                    f"LLM HTTP错误 (attempt {attempt + 1}/{self.max_retries}): "
                    f"status={e.response.status_code}, body={e.response.text[:200]}"
                )
            except httpx.TimeoutException:
                last_error = "timeout"
                logger.warning(
                    f"LLM超时 (attempt {attempt + 1}/{self.max_retries})"
                )
            except httpx.RequestError as e:
                last_error = e
                logger.warning(
                    f"LLM请求错误 (attempt {attempt + 1}/{self.max_retries}): {e}"
                )
            except Exception as e:
                last_error = e
                logger.error(
                    f"LLM未知错误 (attempt {attempt + 1}/{self.max_retries}): {e}"
                )

            # 最后一次尝试不等待
            if attempt < self.max_retries - 1:
                wait_time = self.retry_backoff ** attempt
                await asyncio.sleep(wait_time)

        logger.error(f"LLM调用全部重试失败: {last_error}")
        return None

    async def structured_output(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Dict[str, Any],
        temperature: float = 0.2,
    ) -> Optional[Dict[str, Any]]:
        """
        调用 LLM 并尝试解析为结构化 JSON 输出

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            output_schema: 期望的 JSON schema 示例
            temperature: 温度参数

        Returns:
            解析后的 dict，失败时返回 None
        """
        if not self.enabled:
            return None

        schema_str = json.dumps(output_schema, ensure_ascii=False, indent=2)

        messages = [
            {
                "role": "system",
                "content": (
                    f"{system_prompt}\n\n"
                    f"你必须严格按照以下JSON格式输出，不要输出任何其他内容：\n"
                    f"```json\n{schema_str}\n```"
                ),
            },
            {"role": "user", "content": user_prompt},
        ]

        raw = await self.chat_completion(messages, temperature=temperature)

        if raw is None:
            return None

        # 尝试提取 JSON
        try:
            # 先尝试直接解析
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # 尝试从 markdown 代码块中提取
        import re
        json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 尝试找到第一个 { 和最后一个 }
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw[start:end + 1])
            except json.JSONDecodeError:
                pass

        logger.warning(f"无法从LLM响应中解析JSON: {raw[:500]}")
        return None


# 全局单例
llm_service = LLMService()