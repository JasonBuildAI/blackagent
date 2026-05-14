"""
内容清洗服务

对原始情报进行清洗和去重处理。
支持基于规则和 LLM 增强两种模式。
"""

import logging
import re
import datetime
from typing import Optional, Tuple

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.intelligence import IntelligenceItem
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class CleanerService:
    """内容清洗服务"""

    # 常见噪声模式
    NOISE_PATTERNS = [
        # 转发标记
        r"\[转发\].*?\[/转发\]",
        r"\[引用\].*?\[/引用\]",
        r"Forwarded from.*",
        r"转发的.*消息",
        r"------ 转发 ------",
        # 时间戳噪声
        r"\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}:\d{2}",
        # 系统消息
        r"\[系统消息\].*",
        r"\[群公告\].*",
        r"你撤回了一条消息",
        r"对方撤回了一条消息",
        # HTML 标签
        r"<[^>]+>",
        # 多余空白
        r"\n{3,}",
        r" {3,}",
        # 广告/垃圾
        r"加微信.*免费",
        r"点击链接.*领取",
        r"关注公众号.*福利",
        r"扫码.*红包",
    ]

    @staticmethod
    def clean_content_rule(raw_content: str) -> str:
        """
        基于规则的内容清洗

        步骤：
        1. 去除已知噪声模式
        2. 规范化空白字符
        3. 去除首尾空白
        4. 合并连续空行
        """
        cleaned = raw_content

        # 应用噪声模式
        for pattern in CleanerService.NOISE_PATTERNS:
            cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL | re.IGNORECASE)

        # 规范化空白
        cleaned = re.sub(r"\r\n", "\n", cleaned)
        cleaned = re.sub(r"\r", "\n", cleaned)

        # 合并连续空行为最多两个空行
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

        # 去除每行首尾空白
        lines = [line.strip() for line in cleaned.split("\n")]
        cleaned = "\n".join(lines)

        # 去除首尾空白
        cleaned = cleaned.strip()

        # 如果清洗后内容太短，保留原始内容
        if len(cleaned) < 5:
            cleaned = raw_content.strip()

        return cleaned

    async def clean_content_llm(self, raw_content: str) -> Optional[str]:
        """使用 LLM 进行内容清洗"""
        if not llm_service.enabled:
            return None

        schema = {
            "cleaned_content": "清洗后的核心情报内容，去除无关噪声",
            "noise_removed": ["被去除的噪声片段1", "..."],
            "key_points": ["关键信息点1", "..."],
        }

        result = await llm_service.structured_output(
            system_prompt=(
                "你是一个专业的情报数据清洗助手。请清洗以下黑灰产情报数据，"
                "去除系统消息、转发标记、时间戳噪声、广告垃圾等无关内容，"
                "保留核心情报信息。如果内容本身就是有意义的黑灰产情报，请不要过度清洗。"
            ),
            user_prompt=f"请清洗以下情报内容：\n\n{raw_content}",
            output_schema=schema,
            temperature=0.1,
        )

        if result and "cleaned_content" in result:
            cleaned = result["cleaned_content"].strip()
            if len(cleaned) >= 5:
                return cleaned

        return None

    async def clean_content(
        self,
        db: AsyncSession,
        item: IntelligenceItem,
    ) -> str:
        """
        清洗单条情报内容

        优先使用 LLM，不可用时回退到规则引擎。
        清洗结果会保存到数据库。
        """
        raw = item.raw_content

        # 尝试 LLM 清洗
        cleaned = await self.clean_content_llm(raw)

        # 回退到规则清洗
        if cleaned is None:
            logger.debug("LLM不可用，使用规则引擎清洗内容")
            cleaned = self.clean_content_rule(raw)

        # 保存清洗结果
        item.cleaned_content = cleaned
        await db.flush()

        return cleaned

    async def deduplicate(
        self,
        db: AsyncSession,
        item: IntelligenceItem,
    ) -> bool:
        """
        对单条情报进行去重

        检查内容哈希是否已存在，若存在则标记为重复。
        返回 True 表示该条目是重复的。
        """
        # 检查是否有相同哈希的其他条目
        if not item.content_hash:
            return False

        stmt = select(IntelligenceItem).where(
            IntelligenceItem.content_hash == item.content_hash,
            IntelligenceItem.id != item.id,
            IntelligenceItem.is_duplicate == False,  # noqa: E712
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            item.is_duplicate = True
            item.duplicate_of_id = existing.id
            await db.flush()
            return True

        return False

    async def deduplicate_all_pending(
        self,
        db: AsyncSession,
    ) -> int:
        """
        对数据库中所有未去重的条目进行去重

        Returns:
            发现并标记的重复条目数量
        """
        # 获取所有非重复条目
        stmt = select(IntelligenceItem).where(
            IntelligenceItem.is_duplicate == False,  # noqa: E712
            IntelligenceItem.content_hash.isnot(None),
        ).order_by(IntelligenceItem.ingested_at.asc())

        result = await db.execute(stmt)
        items = result.scalars().all()

        seen_hashes = {}
        duplicates_count = 0

        for item in items:
            if item.content_hash in seen_hashes:
                item.is_duplicate = True
                item.duplicate_of_id = seen_hashes[item.content_hash]
                duplicates_count += 1
            else:
                seen_hashes[item.content_hash] = item.id

        await db.flush()
        logger.info(f"去重完成: 发现 {duplicates_count} 条重复")

        return duplicates_count


# 全局单例
cleaner_service = CleanerService()