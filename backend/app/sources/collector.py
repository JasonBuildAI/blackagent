"""
统一采集调度服务

协调所有数据源的采集工作，将采集到的原始情报存入数据库。
"""

import datetime
import hashlib
import logging
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.intelligence import IntelligenceItem
from app.sources.base import BaseSource, RawIntelligence
from app.sources.web_search import WebSearchSource
from app.sources.rss_feed import RSSFeedSource
from app.sources.hackernews import HackerNewsSource
from app.sources.github_advisory import GitHubAdvisorySource

logger = logging.getLogger(__name__)


class CollectorService:
    """统一采集调度服务"""

    def __init__(self):
        self._sources: Dict[str, BaseSource] = {}
        self._init_sources()

    def _init_sources(self):
        self._sources = {
            "web_search": WebSearchSource(),
            "rss_feed": RSSFeedSource(),
            "hackernews": HackerNewsSource(),
            "github_advisory": GitHubAdvisorySource(),
        }

    def get_available_sources(self) -> List[dict]:
        """获取所有可用数据源信息"""
        sources = []
        for key, source in self._sources.items():
            sources.append({
                "id": key,
                "name": source.name,
                "source_type": source.source_type,
                "description": source.description,
                "requires_api_key": source.requires_api_key,
                "api_key_name": source.api_key_name,
            })
        return sources

    def configure_source(self, source_id: str, **kwargs):
        """配置数据源参数"""
        source = self._sources.get(source_id)
        if not source:
            raise ValueError(f"未知数据源: {source_id}")

        if source_id == "web_search" and "api_key" in kwargs:
            source.set_api_key(kwargs["api_key"])
        elif source_id == "github_advisory" and "github_token" in kwargs:
            source.set_github_token(kwargs["github_token"])

    async def collect_from_source(
        self,
        source_id: str,
        max_items: int = 20,
    ) -> List[RawIntelligence]:
        """从指定数据源采集情报"""
        source = self._sources.get(source_id)
        if not source:
            raise ValueError(f"未知数据源: {source_id}")

        logger.info(f"开始从 {source.name} 采集情报...")
        items = await source.collect(max_items=max_items)
        logger.info(f"从 {source.name} 采集完成: {len(items)} 条")
        return items

    async def collect_all(
        self,
        max_items_per_source: int = 20,
        source_ids: Optional[List[str]] = None,
    ) -> Dict[str, List[RawIntelligence]]:
        """从所有（或指定的）数据源采集情报"""
        results: Dict[str, List[RawIntelligence]] = {}
        targets = source_ids or list(self._sources.keys())

        for source_id in targets:
            try:
                items = await self.collect_from_source(
                    source_id, max_items=max_items_per_source
                )
                results[source_id] = items
            except Exception as e:
                logger.error(f"数据源 {source_id} 采集失败: {e}")
                results[source_id] = []

        return results

    async def collect_and_store(
        self,
        db: AsyncSession,
        source_ids: Optional[List[str]] = None,
        max_items_per_source: int = 20,
    ) -> dict:
        """采集情报并存储到数据库"""
        all_raw = await self.collect_all(
            max_items_per_source=max_items_per_source,
            source_ids=source_ids,
        )

        total_collected = 0
        total_new = 0
        total_duplicates = 0
        source_stats = {}

        for source_id, raw_items in all_raw.items():
            new_count = 0
            dup_count = 0

            for raw in raw_items:
                total_collected += 1
                content_hash = self._compute_hash(raw.raw_content)

                existing_id = await self._check_duplicate(db, content_hash)
                if existing_id:
                    dup_count += 1
                    total_duplicates += 1
                    continue

                new_count += 1
                total_new += 1

                item = IntelligenceItem(
                    source_type=raw.source_type,
                    source_name=raw.source_name,
                    raw_content=raw.raw_content,
                    content_hash=content_hash,
                    is_duplicate=False,
                    duplicate_of_id=None,
                    published_at=raw.published_at or datetime.datetime.utcnow(),
                    ingested_at=datetime.datetime.utcnow(),
                    status="pending",
                )
                db.add(item)
                await db.flush()

            source_stats[source_id] = {
                "collected": len(raw_items),
                "new": new_count,
                "duplicates": dup_count,
            }

        await db.flush()

        return {
            "total_collected": total_collected,
            "total_new": total_new,
            "total_duplicates": total_duplicates,
            "source_stats": source_stats,
        }

    async def test_source(self, source_id: str) -> dict:
        """测试数据源连接"""
        source = self._sources.get(source_id)
        if not source:
            return {"success": False, "message": f"未知数据源: {source_id}"}
        return await source.test_connection()

    @staticmethod
    def _compute_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    async def _check_duplicate(db: AsyncSession, content_hash: str) -> Optional[str]:
        stmt = select(IntelligenceItem.id).where(
            IntelligenceItem.content_hash == content_hash,
            IntelligenceItem.is_duplicate == False,  # noqa: E712
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


collector_service = CollectorService()
