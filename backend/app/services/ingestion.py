"""
情报摄入服务

从多源渠道（IM、群组、公众号、论坛）摄入情报数据。
支持基于规则的摄入和模拟数据生成。
"""

import datetime
import hashlib
import logging
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.intelligence import IntelligenceItem
from app.mock_data.generator import MockDataGenerator

logger = logging.getLogger(__name__)


class IngestionService:
    """情报摄入服务"""

    def __init__(self):
        self.generator = MockDataGenerator()

    @staticmethod
    def compute_content_hash(content: str) -> str:
        """计算内容哈希值用于去重"""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    async def _check_duplicate(
        self, db: AsyncSession, content_hash: str
    ) -> Optional[str]:
        """检查是否已存在相同哈希的情报"""
        stmt = select(IntelligenceItem.id).where(
            IntelligenceItem.content_hash == content_hash,
            IntelligenceItem.is_duplicate == False,  # noqa: E712
        )
        result = await db.execute(stmt)
        existing_id = result.scalar_one_or_none()
        return existing_id

    async def ingest_single(
        self,
        db: AsyncSession,
        source_type: str,
        source_name: str,
        raw_content: str,
        published_at: Optional[datetime.datetime] = None,
    ) -> IntelligenceItem:
        """
        摄入单条情报

        自动计算哈希并检查去重。重复条目会被标记但不阻止摄入。
        """
        content_hash = self.compute_content_hash(raw_content)

        # 去重检查
        duplicate_of_id = await self._check_duplicate(db, content_hash)
        is_duplicate = duplicate_of_id is not None

        item = IntelligenceItem(
            source_type=source_type,
            source_name=source_name,
            raw_content=raw_content,
            content_hash=content_hash,
            is_duplicate=is_duplicate,
            duplicate_of_id=duplicate_of_id,
            published_at=published_at or datetime.datetime.utcnow(),
            ingested_at=datetime.datetime.utcnow(),
            status="pending",
        )

        db.add(item)
        await db.flush()
        return item

    async def ingest_from_mock_sources(
        self,
        db: AsyncSession,
        source_types: Optional[List[str]] = None,
        count: Optional[int] = None,
    ) -> dict:
        """
        从模拟数据源摄入情报

        Args:
            db: 数据库会话
            source_types: 指定来源类型列表，None 表示所有来源
            count: 指定生成数量，None 表示使用默认值

        Returns:
            {"total_generated": N, "new_items": N, "duplicates": N}
        """
        # 生成模拟数据
        mock_items = self.generator.generate(
            source_types=source_types,
            count=count,
        )

        total_generated = len(mock_items)
        new_items = 0
        duplicates = 0

        for mock_item in mock_items:
            content_hash = self.compute_content_hash(mock_item["raw_content"])
            existing_id = await self._check_duplicate(db, content_hash)

            if existing_id is not None:
                duplicates += 1
                continue

            new_items += 1

            item = IntelligenceItem(
                source_type=mock_item["source_type"],
                source_name=mock_item["source_name"],
                raw_content=mock_item["raw_content"],
                content_hash=content_hash,
                is_duplicate=False,
                duplicate_of_id=None,
                published_at=mock_item.get("published_at", datetime.datetime.utcnow()),
                ingested_at=datetime.datetime.utcnow(),
                status="pending",
            )

            db.add(item)
            await db.flush()

        logger.info(
            f"模拟数据摄入完成: 生成={total_generated}, 新增={new_items}, 重复={duplicates}"
        )

        return {
            "total_generated": total_generated,
            "new_items": new_items,
            "duplicates": duplicates,
        }


# 全局单例
ingestion_service = IngestionService()