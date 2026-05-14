"""
设置服务

提供系统设置的读写功能，支持从数据库动态加载配置。
"""

import logging
from typing import Optional, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.settings import SystemSetting

logger = logging.getLogger(__name__)


class SettingsService:
    """设置服务"""

    # 默认设置项
    DEFAULT_SETTINGS = {
        "llm_api_key": {
            "value": "",
            "description": "LLM API 密钥，用于启用大模型分析功能",
        },
        "llm_api_base": {
            "value": "https://api.openai.com/v1",
            "description": "LLM API 基础 URL",
        },
        "llm_model": {
            "value": "gpt-4o-mini",
            "description": "LLM 模型名称",
        },
        "tavily_api_key": {
            "value": "",
            "description": "Tavily API 密钥，用于Web搜索采集威胁情报（免费注册: https://tavily.com）",
        },
        "github_token": {
            "value": "",
            "description": "GitHub Personal Access Token，用于提升GitHub安全公告API速率限制（可选）",
        },
    }

    async def init_default_settings(self, db: AsyncSession) -> None:
        """初始化默认设置"""
        for key, config in self.DEFAULT_SETTINGS.items():
            stmt = select(SystemSetting).where(SystemSetting.key == key)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if not existing:
                setting = SystemSetting(
                    key=key,
                    value=config["value"],
                    description=config["description"],
                )
                db.add(setting)
                logger.info(f"初始化默认设置: {key}")

        await db.flush()

    async def get_setting(self, db: AsyncSession, key: str) -> Optional[str]:
        """获取单个设置值"""
        stmt = select(SystemSetting.value).where(SystemSetting.key == key)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_settings(self, db: AsyncSession) -> Dict[str, Dict]:
        """获取所有设置"""
        stmt = select(SystemSetting)
        result = await db.execute(stmt)
        settings = result.scalars().all()

        return {
            s.key: {
                "value": s.value,
                "description": s.description,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in settings
        }

    async def update_setting(
        self,
        db: AsyncSession,
        key: str,
        value: str,
    ) -> bool:
        """更新设置值"""
        stmt = select(SystemSetting).where(SystemSetting.key == key)
        result = await db.execute(stmt)
        setting = result.scalar_one_or_none()

        if setting:
            setting.value = value
            await db.flush()
            logger.info(f"设置已更新: {key}")
            return True
        else:
            # 如果设置不存在，创建新设置
            setting = SystemSetting(
                key=key,
                value=value,
                description=self.DEFAULT_SETTINGS.get(key, {}).get("description", ""),
            )
            db.add(setting)
            await db.flush()
            logger.info(f"设置已创建: {key}")
            return True

    async def get_llm_config(self, db: AsyncSession) -> Dict[str, str]:
        """获取 LLM 配置"""
        api_key = await self.get_setting(db, "llm_api_key") or ""
        api_base = await self.get_setting(db, "llm_api_base") or "https://api.openai.com/v1"
        model = await self.get_setting(db, "llm_model") or "gpt-4o-mini"

        return {
            "api_key": api_key,
            "api_base": api_base,
            "model": model,
            "enabled": bool(api_key and api_key.strip()),
        }


# 全局单例
settings_service = SettingsService()
