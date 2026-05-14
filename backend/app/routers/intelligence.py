"""
情报 CRUD 路由

提供情报条目的查询、详情、摄入和删除功能。
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.intelligence import IntelligenceItem
from app.models.schemas import (
    IntelligenceItemResponse,
    IntelligenceListResponse,
    EntityResponse,
    AnalysisReportResponse,
    IngestRequest,
    IngestResponse,
    DeleteResponse,
    DashboardStatsResponse,
)
from app.services.ingestion import ingestion_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/intelligence", tags=["情报管理"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """获取仪表盘统计数据"""
    # 总数量
    total_stmt = select(func.count()).select_from(IntelligenceItem)
    total_result = await db.execute(total_stmt)
    total_items = total_result.scalar() or 0

    # 风险等级分布
    risk_stmt = select(
        IntelligenceItem.risk_level,
        func.count()
    ).where(
        IntelligenceItem.risk_level.isnot(None)
    ).group_by(IntelligenceItem.risk_level)
    risk_result = await db.execute(risk_stmt)
    risk_distribution = {row[0]: row[1] for row in risk_result.all()}

    # 来源分布
    source_stmt = select(
        IntelligenceItem.source_type,
        func.count()
    ).group_by(IntelligenceItem.source_type)
    source_result = await db.execute(source_stmt)
    source_distribution = {row[0]: row[1] for row in source_result.all()}

    # 类别分布
    category_stmt = select(
        IntelligenceItem.risk_category,
        func.count()
    ).where(
        IntelligenceItem.risk_category.isnot(None)
    ).group_by(IntelligenceItem.risk_category)
    category_result = await db.execute(category_stmt)
    category_distribution = {row[0]: row[1] for row in category_result.all()}

    # 严重告警数
    critical_stmt = select(func.count()).where(
        IntelligenceItem.risk_level == "critical"
    )
    critical_result = await db.execute(critical_stmt)
    critical_alerts = critical_result.scalar() or 0

    # 已分析数
    analyzed_stmt = select(func.count()).where(
        IntelligenceItem.status == "analyzed"
    )
    analyzed_result = await db.execute(analyzed_stmt)
    analyzed_count = analyzed_result.scalar() or 0

    # 待处理数
    pending_stmt = select(func.count()).where(
        IntelligenceItem.status == "pending"
    )
    pending_result = await db.execute(pending_stmt)
    pending_count = pending_result.scalar() or 0

    # 最近10条情报
    recent_stmt = select(IntelligenceItem).order_by(
        IntelligenceItem.ingested_at.desc()
    ).limit(10)
    recent_result = await db.execute(recent_stmt)
    recent_items_raw = recent_result.scalars().all()

    recent_items = []
    for item in recent_items_raw:
        entities_response = None
        if item.entities:
            entities_response = [
                EntityResponse.model_validate(e) for e in item.entities
            ]

        analysis_response = None
        if item.analysis_report:
            analysis_response = AnalysisReportResponse.model_validate(
                item.analysis_report
            )

        recent_items.append(
            IntelligenceItemResponse(
                id=item.id,
                source_type=item.source_type,
                source_name=item.source_name,
                raw_content=item.raw_content,
                cleaned_content=item.cleaned_content,
                content_hash=item.content_hash,
                risk_level=item.risk_level,
                risk_category=item.risk_category,
                status=item.status,
                is_duplicate=item.is_duplicate,
                duplicate_of_id=item.duplicate_of_id,
                published_at=item.published_at,
                ingested_at=item.ingested_at,
                analyzed_at=item.analyzed_at,
                created_at=item.created_at,
                entities=entities_response,
                analysis_report=analysis_response,
            )
        )

    return DashboardStatsResponse(
        total_items=total_items,
        risk_distribution=risk_distribution,
        source_distribution=source_distribution,
        category_distribution=category_distribution,
        recent_items=recent_items,
        critical_alerts=critical_alerts,
        analyzed_count=analyzed_count,
        pending_count=pending_count,
    )


@router.get("", response_model=IntelligenceListResponse)
async def list_intelligence(
    source_type: Optional[str] = Query(None, description="来源类型筛选"),
    risk_level: Optional[str] = Query(None, description="风险等级筛选"),
    risk_category: Optional[str] = Query(None, description="风险类别筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    is_duplicate: Optional[bool] = Query(None, description="是否重复"),
    search: Optional[str] = Query(None, description="内容搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
):
    """获取情报列表，支持多条件筛选和分页"""
    # 构建查询
    stmt = select(IntelligenceItem)

    # 筛选条件
    if source_type:
        stmt = stmt.where(IntelligenceItem.source_type == source_type)
    if risk_level:
        stmt = stmt.where(IntelligenceItem.risk_level == risk_level)
    if risk_category:
        stmt = stmt.where(IntelligenceItem.risk_category == risk_category)
    if status:
        stmt = stmt.where(IntelligenceItem.status == status)
    if is_duplicate is not None:
        stmt = stmt.where(IntelligenceItem.is_duplicate == is_duplicate)
    if search:
        stmt = stmt.where(
            or_(
                IntelligenceItem.raw_content.ilike(f"%{search}%"),
                IntelligenceItem.cleaned_content.ilike(f"%{search}%"),
                IntelligenceItem.source_name.ilike(f"%{search}%"),
            )
        )

    # 计算总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # 分页和排序
    stmt = stmt.order_by(IntelligenceItem.ingested_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    items = result.scalars().all()

    # 构建响应
    item_responses = []
    for item in items:
        # 手动构建响应以避免循环引用问题
        entities_response = None
        if item.entities:
            entities_response = [
                EntityResponse.model_validate(e) for e in item.entities
            ]

        analysis_response = None
        if item.analysis_report:
            analysis_response = AnalysisReportResponse.model_validate(
                item.analysis_report
            )

        item_responses.append(
            IntelligenceItemResponse(
                id=item.id,
                source_type=item.source_type,
                source_name=item.source_name,
                raw_content=item.raw_content,
                cleaned_content=item.cleaned_content,
                content_hash=item.content_hash,
                risk_level=item.risk_level,
                risk_category=item.risk_category,
                status=item.status,
                is_duplicate=item.is_duplicate,
                duplicate_of_id=item.duplicate_of_id,
                published_at=item.published_at,
                ingested_at=item.ingested_at,
                analyzed_at=item.analyzed_at,
                created_at=item.created_at,
                entities=entities_response,
                analysis_report=analysis_response,
            )
        )

    return IntelligenceListResponse(
        items=item_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{intelligence_id}", response_model=IntelligenceItemResponse)
async def get_intelligence(
    intelligence_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取单条情报详情，包含关联实体"""
    stmt = select(IntelligenceItem).where(IntelligenceItem.id == intelligence_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail=f"情报不存在: {intelligence_id}")

    entities_response = None
    if item.entities:
        entities_response = [
            EntityResponse.model_validate(e) for e in item.entities
        ]

    analysis_response = None
    if item.analysis_report:
        analysis_response = AnalysisReportResponse.model_validate(
            item.analysis_report
        )

    return IntelligenceItemResponse(
        id=item.id,
        source_type=item.source_type,
        source_name=item.source_name,
        raw_content=item.raw_content,
        cleaned_content=item.cleaned_content,
        content_hash=item.content_hash,
        risk_level=item.risk_level,
        risk_category=item.risk_category,
        status=item.status,
        is_duplicate=item.is_duplicate,
        duplicate_of_id=item.duplicate_of_id,
        published_at=item.published_at,
        ingested_at=item.ingested_at,
        analyzed_at=item.analyzed_at,
        created_at=item.created_at,
        entities=entities_response,
        analysis_report=analysis_response,
    )


@router.post("/ingest", response_model=IngestResponse)
async def ingest_intelligence(
    request: Optional[IngestRequest] = None,
    db: AsyncSession = Depends(get_db),
):
    """触发模拟数据摄入"""
    if request is None:
        request = IngestRequest()

    result = await ingestion_service.ingest_from_mock_sources(
        db=db,
        source_types=request.source_types,
        count=request.count,
    )

    return IngestResponse(
        total_generated=result["total_generated"],
        new_items=result["new_items"],
        duplicates=result["duplicates"],
        message=(
            f"摄入完成：生成 {result['total_generated']} 条，"
            f"新增 {result['new_items']} 条，"
            f"重复 {result['duplicates']} 条"
        ),
    )


@router.delete("/{intelligence_id}", response_model=DeleteResponse)
async def delete_intelligence(
    intelligence_id: str,
    db: AsyncSession = Depends(get_db),
):
    """删除单条情报及其关联数据"""
    stmt = select(IntelligenceItem).where(IntelligenceItem.id == intelligence_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail=f"情报不存在: {intelligence_id}")

    await db.delete(item)
    await db.flush()

    return DeleteResponse(
        success=True,
        message=f"情报 {intelligence_id} 已删除",
    )