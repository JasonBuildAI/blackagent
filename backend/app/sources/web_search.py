"""
Web Search 数据源

通过 Tavily API 或兼容的搜索 API 搜索公开的黑灰产威胁情报。
所有搜索均基于公开信息，不涉及非法数据获取。

Tavily API 是专为 AI Agent 设计的搜索 API，免费额度 1000 次/月。
注册地址: https://tavily.com
"""

import datetime
import json
import logging
from typing import List, Optional

import httpx

from app.sources.base import BaseSource, RawIntelligence

logger = logging.getLogger(__name__)

SEARCH_QUERIES = [
    "黑灰产 作弊工具 最新动态",
    "网络黑产 数据泄露 2024 2025",
    "钓鱼攻击 新手法 预警",
    "恶意软件 传播渠道 分析",
    "账号交易 黑产 产业链",
    "诈骗技术 新模式 防范",
    "cybercrime dark web threat intelligence",
    "fraud technique phishing scam alert",
    "malware distribution ransomware attack",
    "data breach leak credential stuffing",
]

TAVILY_API_URL = "https://api.tavily.com/search"


class WebSearchSource(BaseSource):
    """Web 搜索数据源"""

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def source_type(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Web搜索 - 通过Tavily API搜索公开威胁情报"

    @property
    def requires_api_key(self) -> bool:
        return True

    @property
    def api_key_name(self) -> Optional[str]:
        return "tavily_api_key"

    def set_api_key(self, api_key: str):
        self._api_key = api_key

    async def collect(self, max_items: int = 20) -> List[RawIntelligence]:
        if not self._api_key:
            logger.warning("Tavily API Key 未配置，跳过 Web 搜索采集")
            return []

        all_items: List[RawIntelligence] = []
        queries = SEARCH_QUERIES[:3]

        for query in queries:
            try:
                items = await self._search(query, max_items=max_items // len(queries) + 1)
                all_items.extend(items)
            except Exception as e:
                logger.error(f"Web搜索失败 (query={query}): {e}")

        return all_items[:max_items]

    async def _search(self, query: str, max_items: int = 10) -> List[RawIntelligence]:
        payload = {
            "api_key": self._api_key,
            "query": query,
            "max_results": max_items,
            "include_raw_content": True,
            "search_depth": "advanced",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(TAVILY_API_URL, json=payload)
            response.raise_for_status()
            data = response.json()

        results = data.get("results", [])
        items: List[RawIntelligence] = []

        for result in results:
            content = result.get("raw_content") or result.get("content") or ""
            if not content or len(content.strip()) < 20:
                continue

            published_at = None
            if result.get("published_date"):
                try:
                    published_at = datetime.datetime.fromisoformat(
                        result["published_date"].replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

            items.append(
                RawIntelligence(
                    source_type=self.source_type,
                    source_name=f"Web搜索: {query}",
                    raw_content=content.strip()[:5000],
                    published_at=published_at,
                    url=result.get("url", ""),
                    author=result.get("author", ""),
                    tags=[query],
                )
            )

        logger.info(f"Web搜索采集: query='{query}', 获取 {len(items)} 条")
        return items

    async def search_custom(self, query: str, max_items: int = 10) -> List[RawIntelligence]:
        """自定义搜索查询"""
        if not self._api_key:
            raise ValueError("Tavily API Key 未配置")
        return await self._search(query, max_items)
