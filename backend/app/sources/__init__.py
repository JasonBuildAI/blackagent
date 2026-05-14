"""
数据源采集模块

提供从多源渠道采集黑灰产情报的能力：
- Web Search: 通过 Tavily/搜索引擎搜索公开威胁情报
- RSS Feed: 订阅安全资讯 RSS 源
- HackerNews: 采集安全相关新闻
- GitHub Advisory: 采集安全公告
"""

from app.sources.base import BaseSource, RawIntelligence
from app.sources.web_search import WebSearchSource
from app.sources.rss_feed import RSSFeedSource
from app.sources.hackernews import HackerNewsSource
from app.sources.github_advisory import GitHubAdvisorySource
from app.sources.collector import collector_service

__all__ = [
    "BaseSource",
    "RawIntelligence",
    "WebSearchSource",
    "RSSFeedSource",
    "HackerNewsSource",
    "GitHubAdvisorySource",
    "collector_service",
]
