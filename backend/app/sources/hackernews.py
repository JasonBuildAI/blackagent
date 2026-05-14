"""
HackerNews API 数据源

通过 HackerNews 公开 API 采集安全相关的新闻和讨论。
API 文档: https://github.com/HackerNews/API
无需 API Key，完全公开。
"""

import datetime
import logging
from typing import List, Optional

import httpx

from app.sources.base import BaseSource, RawIntelligence

logger = logging.getLogger(__name__)

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"

SECURITY_KEYWORDS = [
    "security", "malware", "ransomware", "phishing", "vulnerability",
    "exploit", "breach", "hack", "cyber", "threat", "privacy",
    "encryption", "password", "authentication", "zero-day", "0day",
    "botnet", "trojan", "backdoor", "dark web", "fraud", "scam",
    "data leak", "credential", "ddos", "supply chain attack",
    "cybercrime", "identity theft", "social engineering",
]

STORY_TYPES = ["topstories", "newstories"]


class HackerNewsSource(BaseSource):
    """HackerNews 数据源"""

    @property
    def name(self) -> str:
        return "hackernews"

    @property
    def source_type(self) -> str:
        return "forum"

    @property
    def description(self) -> str:
        return "HackerNews - 采集安全相关的技术新闻和讨论"

    @property
    def requires_api_key(self) -> bool:
        return False

    async def collect(self, max_items: int = 20) -> List[RawIntelligence]:
        all_items: List[RawIntelligence] = []

        for story_type in STORY_TYPES:
            try:
                story_ids = await self._get_story_ids(story_type, limit=100)
                items = await self._collect_stories(story_ids, max_items=max_items)
                all_items.extend(items)
            except Exception as e:
                logger.error(f"HackerNews采集失败 ({story_type}): {e}")

        seen_titles = set()
        unique_items = []
        for item in all_items:
            title_key = item.raw_content[:50].lower()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_items.append(item)

        return unique_items[:max_items]

    async def _get_story_ids(self, story_type: str, limit: int = 100) -> List[int]:
        async with httpx.AsyncClient(timeout=15, proxy=None) as client:
            response = await client.get(f"{HN_API_BASE}/{story_type}.json")
            response.raise_for_status()
            ids = response.json()
            return ids[:limit]

    async def _collect_stories(
        self, story_ids: List[int], max_items: int = 10
    ) -> List[RawIntelligence]:
        items: List[RawIntelligence] = []

        for story_id in story_ids:
            if len(items) >= max_items:
                break

            try:
                story = await self._get_item(story_id)
                if not story or story.get("type") != "story":
                    continue
                if not story.get("title"):
                    continue

                title = story["title"]
                if not self._is_security_related(title):
                    continue

                content = title
                if story.get("text"):
                    content += f"\n\n{story['text']}"
                url = story.get("url", f"https://news.ycombinator.com/item?id={story_id}")

                published_at = None
                if story.get("time"):
                    published_at = datetime.datetime.fromtimestamp(story["time"])

                items.append(
                    RawIntelligence(
                        source_type=self.source_type,
                        source_name="HackerNews",
                        raw_content=content.strip()[:5000],
                        published_at=published_at,
                        url=url,
                        author=story.get("by", ""),
                        tags=["hackernews", "security"],
                    )
                )
            except Exception as e:
                logger.debug(f"HackerNews item {story_id} 获取失败: {e}")

        logger.info(f"HackerNews采集: 获取 {len(items)} 条安全相关新闻")
        return items

    async def _get_item(self, item_id: int) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=10, proxy=None) as client:
            response = await client.get(f"{HN_API_BASE}/item/{item_id}.json")
            response.raise_for_status()
            return response.json()

    def _is_security_related(self, text: str) -> bool:
        text_lower = text.lower()
        for kw in SECURITY_KEYWORDS:
            if kw in text_lower:
                return True
        return False
