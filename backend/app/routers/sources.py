"""
数据源管理路由

提供数据源列表查询、采集触发、连接测试等功能。
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.sources.collector import collector_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sources", tags=["数据源管理"])


class SourceInfo(BaseModel):
    id: str
    name: str
    source_type: str
    description: str
    requires_api_key: bool
    api_key_name: Optional[str] = None


class SourceListResponse(BaseModel):
    sources: List[SourceInfo]


class CollectRequest(BaseModel):
    source_ids: Optional[List[str]] = Field(
        None,
        description="指定采集的数据源ID列表，为空则采集所有",
    )
    max_items_per_source: int = Field(
        20,
        ge=1,
        le=100,
        description="每个数据源最大采集数量",
    )


class SourceStats(BaseModel):
    collected: int = 0
    new: int = 0
    duplicates: int = 0


class CollectResponse(BaseModel):
    total_collected: int = Field(..., description="总采集数")
    total_new: int = Field(..., description="新增数")
    total_duplicates: int = Field(..., description="重复数")
    source_stats: dict = Field(default_factory=dict, description="各数据源统计")
    message: str = Field(..., description="结果描述")


class TestResponse(BaseModel):
    success: bool
    message: str
    items_count: int = 0


@router.get("", response_model=SourceListResponse)
async def list_sources():
    """获取所有可用数据源"""
    sources = collector_service.get_available_sources()
    return SourceListResponse(
        sources=[SourceInfo(**s) for s in sources]
    )


@router.post("/collect", response_model=CollectResponse)
async def collect_intelligence(
    request: CollectRequest,
    db: AsyncSession = Depends(get_db),
):
    """从数据源采集情报并存储到数据库"""
    try:
        await _configure_sources_from_db(db)

        result = await collector_service.collect_and_store(
            db=db,
            source_ids=request.source_ids,
            max_items_per_source=request.max_items_per_source,
        )
        await db.commit()

        return CollectResponse(
            total_collected=result["total_collected"],
            total_new=result["total_new"],
            total_duplicates=result["total_duplicates"],
            source_stats=result["source_stats"],
            message=(
                f"采集完成：共采集 {result['total_collected']} 条，"
                f"新增 {result['total_new']} 条，"
                f"重复 {result['total_duplicates']} 条"
            ),
        )
    except Exception as e:
        logger.error(f"采集失败: {e}")
        raise HTTPException(status_code=500, detail=f"采集失败: {str(e)}")


@router.post("/{source_id}/test", response_model=TestResponse)
async def test_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),
):
    """测试数据源连接"""
    await _configure_sources_from_db(db)

    result = await collector_service.test_source(source_id)
    return TestResponse(
        success=result["success"],
        message=result["message"],
        items_count=result.get("items_count", 0),
    )


async def _configure_sources_from_db(db: AsyncSession):
    """从数据库加载 API Key 配置到数据源"""
    from app.services.settings_service import settings_service

    tavily_key = await settings_service.get_setting(db, "tavily_api_key")
    if tavily_key:
        collector_service.configure_source("web_search", api_key=tavily_key)

    github_token = await settings_service.get_setting(db, "github_token")
    if github_token:
        collector_service.configure_source("github_advisory", github_token=github_token)
