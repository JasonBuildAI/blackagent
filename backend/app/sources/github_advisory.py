"""
GitHub Security Advisories 数据源

通过 GitHub 公开 API 采集安全公告信息。
API 文档: https://docs.github.com/en/rest/security-advisories
无需 API Key 即可访问公开安全公告（有速率限制）。
"""

import datetime
import logging
from typing import List, Optional

import httpx

from app.sources.base import BaseSource, RawIntelligence

logger = logging.getLogger(__name__)

GH_API_BASE = "https://api.github.com"

ADVISORY_KEYWORDS = [
    "malware", "ransomware", "phishing", "exploit", "vulnerability",
    "injection", "xss", "csrf", "rce", "privilege escalation",
    "authentication bypass", "data leak", "credential", "backdoor",
    "supply chain", "dependency confusion", "typosquatting",
]

ECOSYSTEMS = ["pip", "npm", "maven", "nuget", "rubygems", "go", "rust"]


class GitHubAdvisorySource(BaseSource):
    """GitHub 安全公告数据源"""

    def __init__(self, github_token: Optional[str] = None):
        self._github_token = github_token

    @property
    def name(self) -> str:
        return "github_advisory"

    @property
    def source_type(self) -> str:
        return "forum"

    @property
    def description(self) -> str:
        return "GitHub安全公告 - 采集开源生态安全漏洞和恶意包信息"

    @property
    def requires_api_key(self) -> bool:
        return False

    @property
    def api_key_name(self) -> Optional[str]:
        return "github_token"

    def set_github_token(self, token: str):
        self._github_token = token

    async def collect(self, max_items: int = 20) -> List[RawIntelligence]:
        items: List[RawIntelligence] = []

        try:
            global_advisories = await self._collect_global_advisories(max_items=max_items)
            items.extend(global_advisories)
        except Exception as e:
            logger.error(f"GitHub全局公告采集失败: {e}")

        if len(items) < max_items:
            try:
                malware_items = await self._collect_malware_packages(
                    max_items=max_items - len(items)
                )
                items.extend(malware_items)
            except Exception as e:
                logger.error(f"GitHub恶意包采集失败: {e}")

        return items[:max_items]

    async def _collect_global_advisories(
        self, max_items: int = 15
    ) -> List[RawIntelligence]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "BlackAgent-Intelligence-Collector",
        }
        if self._github_token:
            headers["Authorization"] = f"token {self._github_token}"

        params = {
            "per_page": min(max_items, 100),
            "sort": "published",
            "direction": "desc",
            "type": "reviewed",
        }

        async with httpx.AsyncClient(timeout=20, proxy=None) as client:
            response = await client.get(
                f"{GH_API_BASE}/advisories",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            advisories = response.json()

        items: List[RawIntelligence] = []
        for adv in advisories:
            ghsa_id = adv.get("ghsa_id", "")
            summary = adv.get("summary", "")
            description = adv.get("description", "")
            severity = adv.get("severity", "")
            cve_id = adv.get("cve_id", "")
            published_at_str = adv.get("published_at", "")
            html_url = adv.get("html_url", "")
            ecosystem = ""
            vulns = adv.get("vulnerabilities", [])
            if vulns:
                ecosystem = vulns[0].get("package", {}).get("ecosystem", "")

            content_parts = []
            if cve_id:
                content_parts.append(f"[{cve_id}]")
            if ghsa_id:
                content_parts.append(f"GHSA: {ghsa_id}")
            if severity:
                content_parts.append(f"严重程度: {severity}")
            if ecosystem:
                content_parts.append(f"生态: {ecosystem}")
            content_parts.append(f"\n{summary}")
            if description:
                content_parts.append(f"\n\n详细描述:\n{description}")

            content = "\n".join(content_parts)
            if len(content.strip()) < 20:
                continue

            published_at = None
            if published_at_str:
                try:
                    published_at = datetime.datetime.fromisoformat(
                        published_at_str.replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

            tags = ["github_advisory"]
            if severity:
                tags.append(severity.lower())
            if ecosystem:
                tags.append(ecosystem.lower())

            items.append(
                RawIntelligence(
                    source_type=self.source_type,
                    source_name="GitHub安全公告",
                    raw_content=content.strip()[:5000],
                    published_at=published_at,
                    url=html_url,
                    tags=tags,
                )
            )

        logger.info(f"GitHub安全公告采集: 获取 {len(items)} 条")
        return items

    async def _collect_malware_packages(
        self, max_items: int = 10
    ) -> List[RawIntelligence]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "BlackAgent-Intelligence-Collector",
        }
        if self._github_token:
            headers["Authorization"] = f"token {self._github_token}"

        params = {
            "per_page": min(max_items, 50),
            "sort": "published",
            "direction": "desc",
            "type": "malware",
        }

        try:
            async with httpx.AsyncClient(timeout=20, proxy=None) as client:
                response = await client.get(
                    f"{GH_API_BASE}/advisories",
                    headers=headers,
                    params=params,
                )
                response.raise_for_status()
                advisories = response.json()
        except Exception as e:
            logger.warning(f"GitHub恶意包采集失败: {e}")
            return []

        items: List[RawIntelligence] = []
        for adv in advisories:
            ghsa_id = adv.get("ghsa_id", "")
            summary = adv.get("summary", "")
            description = adv.get("description", "")
            html_url = adv.get("html_url", "")
            published_at_str = adv.get("published_at", "")

            content = f"[恶意软件包] GHSA: {ghsa_id}\n\n{summary}"
            if description:
                content += f"\n\n{description}"

            published_at = None
            if published_at_str:
                try:
                    published_at = datetime.datetime.fromisoformat(
                        published_at_str.replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

            items.append(
                RawIntelligence(
                    source_type=self.source_type,
                    source_name="GitHub恶意包",
                    raw_content=content.strip()[:5000],
                    published_at=published_at,
                    url=html_url,
                    tags=["github_malware", "supply_chain"],
                )
            )

        logger.info(f"GitHub恶意包采集: 获取 {len(items)} 条")
        return items
