"""
RSS Feed 数据源

从安全资讯网站的 RSS/Atom 订阅源采集公开威胁情报。
所有数据来源均为公开可访问的安全资讯网站。

支持的 RSS 源:
- 安全客 (aq.mk): 阿里云安全资讯
- FreeBuf: 网络安全行业门户
- 先知社区: 阿里云安全社区
- 看雪论坛: 安全逆向社区
- Krebs on Security: 网络安全调查报道
- The Hacker News: 安全新闻
- BleepingComputer: 安全资讯
- Threatpost: 威胁情报新闻
"""

import datetime
import logging
import re
from typing import List, Optional
from urllib.parse import urlparse

import feedparser
import httpx
from bs4 import BeautifulSoup

from app.sources.base import BaseSource, RawIntelligence

logger = logging.getLogger(__name__)

DEFAULT_RSS_FEEDS = [
    {
        "name": "安全客",
        "url": "https://api.anquanke.com/data/v1/rss",
        "source_type": "public_account",
        "language": "zh",
    },
    {
        "name": "FreeBuf",
        "url": "https://www.freebuf.com/feed",
        "source_type": "forum",
        "language": "zh",
    },
    {
        "name": "先知社区",
        "url": "https://xz.aliyun.com/feed",
        "source_type": "forum",
        "language": "zh",
    },
    {
        "name": "Krebs on Security",
        "url": "https://krebsonsecurity.com/feed/",
        "source_type": "public_account",
        "language": "en",
    },
    {
        "name": "The Hacker News",
        "url": "https://feeds.feedburner.com/TheHackersNews",
        "source_type": "public_account",
        "language": "en",
    },
    {
        "name": "BleepingComputer",
        "url": "https://www.bleepingcomputer.com/feed/",
        "source_type": "public_account",
        "language": "en",
    },
    {
        "name": "Threatpost",
        "url": "https://threatpost.com/feed/",
        "source_type": "public_account",
        "language": "en",
    },
    {
        "name": "Security Affairs",
        "url": "https://securityaffairs.co/wordpress/feed",
        "source_type": "public_account",
        "language": "en",
    },
]

BLACKLIST_KEYWORDS = [
    "ctf", "writeup", "比赛", "招聘", "求职", "培训", "课程",
    "certification", "认证", "考试",
]

THREAT_KEYWORDS_ZH = [
    "漏洞", "攻击", "恶意", "木马", "后门", "钓鱼", "诈骗", "勒索",
    "黑产", "灰产", "数据泄露", "入侵", "渗透", "挖矿", "僵尸网络",
    "0day", "CVE", "exploit", "恶意软件", "勒索软件", "供应链攻击",
    "身份盗窃", "社工", "仿冒", "暗网", "黑市",
]

THREAT_KEYWORDS_EN = [
    "malware", "ransomware", "phishing", "exploit", "vulnerability",
    "breach", "attack", "trojan", "backdoor", "botnet", "fraud",
    "scam", "dark web", "credential", "theft", "injection",
    "0day", "CVE", "threat", "malicious", "hack",
]


class RSSFeedSource(BaseSource):
    """RSS Feed 数据源"""

    def __init__(self, custom_feeds: Optional[List[dict]] = None):
        self._feeds = custom_feeds or DEFAULT_RSS_FEEDS

    @property
    def name(self) -> str:
        return "rss_feed"

    @property
    def source_type(self) -> str:
        return "rss_feed"

    @property
    def description(self) -> str:
        return "RSS订阅 - 从安全资讯网站采集公开威胁情报"

    @property
    def requires_api_key(self) -> bool:
        return False

    async def collect(self, max_items: int = 20) -> List[RawIntelligence]:
        all_items: List[RawIntelligence] = []
        per_feed = max(3, max_items // len(self._feeds))

        for feed_config in self._feeds:
            try:
                items = await self._collect_feed(feed_config, max_items=per_feed)
                all_items.extend(items)
            except Exception as e:
                logger.warning(f"RSS采集失败 ({feed_config['name']}): {e}")

        all_items.sort(key=lambda x: x.published_at or datetime.datetime.min, reverse=True)
        return all_items[:max_items]

    async def _collect_feed(
        self, feed_config: dict, max_items: int = 5
    ) -> List[RawIntelligence]:
        feed_url = feed_config["url"]
        feed_name = feed_config["name"]
        source_type = feed_config.get("source_type", "forum")
        language = feed_config.get("language", "zh")

        try:
            async with httpx.AsyncClient(
                timeout=15,
                follow_redirects=True,
                proxy=None,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            ) as client:
                response = await client.get(feed_url)
                response.raise_for_status()
                feed_data = feedparser.parse(response.text)
        except Exception as e:
            logger.warning(f"RSS获取失败 ({feed_name}): {e}")
            return []

        items: List[RawIntelligence] = []
        entries = feed_data.entries[:max_items * 2]

        for entry in entries:
            title = getattr(entry, "title", "")
            summary = getattr(entry, "summary", "")
            link = getattr(entry, "link", "")
            author = getattr(entry, "author", "")
            published = getattr(entry, "published_parsed", None)

            content = self._extract_text(title, summary)
            if not content or len(content.strip()) < 30:
                continue

            if not self._is_threat_related(content, language):
                continue

            published_at = None
            if published:
                try:
                    published_at = datetime.datetime(*published[:6])
                except (TypeError, ValueError):
                    pass

            items.append(
                RawIntelligence(
                    source_type=source_type,
                    source_name=f"{feed_name}",
                    raw_content=content.strip()[:5000],
                    published_at=published_at,
                    url=link,
                    author=author,
                    tags=[feed_name.lower().replace(" ", "_")],
                )
            )

            if len(items) >= max_items:
                break

        logger.info(f"RSS采集: {feed_name}, 获取 {len(items)} 条")
        return items

    def _extract_text(self, title: str, summary: str) -> str:
        if summary:
            soup = BeautifulSoup(summary, "lxml")
            text = soup.get_text(separator="\n", strip=True)
            if title:
                text = f"{title}\n\n{text}"
            return text
        return title

    def _is_threat_related(self, content: str, language: str) -> bool:
        content_lower = content.lower()

        for kw in BLACKLIST_KEYWORDS:
            if kw.lower() in content_lower:
                return False

        if language == "zh":
            keywords = THREAT_KEYWORDS_ZH
        else:
            keywords = THREAT_KEYWORDS_EN

        content_lower = content.lower()
        for kw in keywords:
            if kw.lower() in content_lower:
                return True

        return False

    @property
    def feed_list(self) -> List[dict]:
        return self._feeds
