"""
数据源基类

定义所有数据源的统一接口和数据结构。
"""

import abc
import datetime
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RawIntelligence:
    """采集到的原始情报数据"""

    source_type: str
    source_name: str
    raw_content: str
    published_at: Optional[datetime.datetime] = None
    url: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)


class BaseSource(abc.ABC):
    """数据源抽象基类"""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """数据源名称"""

    @property
    @abc.abstractmethod
    def source_type(self) -> str:
        """对应 IntelligenceItem.source_type 的值"""

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """数据源描述"""

    @property
    def requires_api_key(self) -> bool:
        """是否需要 API Key"""
        return False

    @property
    def api_key_name(self) -> Optional[str]:
        """API Key 在系统设置中的键名"""
        return None

    @abc.abstractmethod
    async def collect(self, max_items: int = 20) -> List[RawIntelligence]:
        """
        从数据源采集情报

        Args:
            max_items: 最大采集数量

        Returns:
            采集到的原始情报列表
        """

    async def test_connection(self) -> dict:
        """测试数据源连接是否可用"""
        try:
            items = await self.collect(max_items=1)
            return {
                "success": True,
                "message": f"连接成功，获取到 {len(items)} 条数据",
                "items_count": len(items),
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"连接失败: {str(e)}",
                "items_count": 0,
            }
