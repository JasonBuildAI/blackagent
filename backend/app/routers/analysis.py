"""
分析路由

提供情报分析功能：单条分析、批量分析、获取分析报告。
分析流程：清洗 -> 分类 -> 实体提取 -> 深度分析
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.intelligence import IntelligenceItem, AnalysisReport
from app.models.schemas import (
    AnalysisReportResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
)
from app.services.cleaner import cleaner_service
from app.services.classifier import classifier_service
from app.services.extractor import extractor_service
from app.services.analyzer import analyzer_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["情报分析"])


@router.post("/{intelligence_id}", response_model=AnalysisReportResponse)
async def analyze_single(
    intelligence_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    对单条情报执行完整分析流程：
    1. 内容清洗
    2. 风险分类
    3. 实体提取
    4. 深度分析（生成分析报告）
    """
    # 获取情报
    stmt = select(IntelligenceItem).where(IntelligenceItem.id == intelligence_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail=f"情报不存在: {intelligence_id}")

    if item.is_duplicate:
        raise HTTPException(
            status_code=400,
            detail=f"该情报已被标记为重复，无法分析。请先处理重复项。",
        )

    try:
        # 1. 清洗内容
        logger.info(f"开始清洗: {intelligence_id}")
        await cleaner_service.clean_content(db, item)

        # 2. 风险分类
        logger.info(f"开始分类: {intelligence_id}")
        await classifier_service.classify(db, item)

        # 3. 实体提取
        logger.info(f"开始提取实体: {intelligence_id}")
        await extractor_service.extract(db, item)

        # 4. 深度分析
        logger.info(f"开始深度分析: {intelligence_id}")
        report = await analyzer_service.analyze(db, item)

        # 刷新以获取关联数据
        await db.refresh(item)

        return AnalysisReportResponse.model_validate(report)

    except Exception as e:
        logger.error(f"分析失败 {intelligence_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}",
        )


@router.post("/batch", response_model=BatchAnalyzeResponse)
async def analyze_batch(
    request: BatchAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    批量分析情报

    支持两种方式：
    1. 指定 ID 列表
    2. 按 source_type + risk_level 筛选
    """
    ids_to_analyze = []

    if request.intelligence_ids:
        ids_to_analyze = request.intelligence_ids
    else:
        # 按条件筛选未分析的情报
        stmt = select(IntelligenceItem.id).where(
            IntelligenceItem.status != "analyzed",
            IntelligenceItem.is_duplicate == False,  # noqa: E712
        )
        if request.source_type:
            stmt = stmt.where(IntelligenceItem.source_type == request.source_type)
        if request.risk_level:
            stmt = stmt.where(IntelligenceItem.risk_level == request.risk_level)
        stmt = stmt.limit(50)

        result = await db.execute(stmt)
        ids_to_analyze = [row[0] for row in result.all()]

    if not ids_to_analyze:
        return BatchAnalyzeResponse(
            total=0,
            analyzed=0,
            skipped=0,
            errors=["没有找到需要分析的情报"],
        )

    # 对每个条目执行完整分析流程
    total = len(ids_to_analyze)
    analyzed = 0
    skipped = 0
    errors = []

    for item_id in ids_to_analyze:
        try:
            stmt = select(IntelligenceItem).where(IntelligenceItem.id == item_id)
            result = await db.execute(stmt)
            item = result.scalar_one_or_none()

            if not item:
                errors.append(f"ID={item_id}: 情报不存在")
                continue

            if item.status == "analyzed":
                skipped += 1
                continue

            if item.is_duplicate:
                skipped += 1
                continue

            # 完整分析流程
            await cleaner_service.clean_content(db, item)
            await classifier_service.classify(db, item)
            await extractor_service.extract(db, item)
            await analyzer_service.analyze(db, item)

            analyzed += 1

        except Exception as e:
            errors.append(f"ID={item_id}: {str(e)}")
            logger.error(f"批量分析错误 ID={item_id}: {e}")

    return BatchAnalyzeResponse(
        total=total,
        analyzed=analyzed,
        skipped=skipped,
        errors=errors,
    )


@router.get("/{intelligence_id}", response_model=AnalysisReportResponse)
async def get_analysis_report(
    intelligence_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取指定情报的分析报告"""
    stmt = select(AnalysisReport).where(
        AnalysisReport.intelligence_id == intelligence_id
    )
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"分析报告不存在: {intelligence_id}，请先执行分析。",
        )

    return AnalysisReportResponse.model_validate(report)