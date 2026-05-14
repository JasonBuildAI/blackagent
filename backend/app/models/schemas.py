"""
Pydantic v2 数据校验模型

定义所有 API 请求/响应的数据结构。
"""

import datetime
from typing import Optional, List, Dict

from pydantic import BaseModel, Field


# ============================================================================
# IntelligenceItem Schemas
# ============================================================================


class IntelligenceItemCreate(BaseModel):
    """创建情报条目请求"""
    source_type: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="来源类型: im, group, public_account, forum",
    )
    source_name: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="来源名称",
    )
    raw_content: str = Field(
        ...,
        min_length=1,
        description="原始情报内容",
    )
    published_at: Optional[datetime.datetime] = Field(
        None,
        description="情报发布时间",
    )


class EntityResponse(BaseModel):
    """实体响应"""
    id: str
    entity_type: str
    entity_value: str
    entity_context: Optional[str] = None
    confidence: float
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class EntityListResponse(BaseModel):
    """实体列表响应"""
    items: List[EntityResponse]
    total: int


class AnalysisReportResponse(BaseModel):
    """分析报告响应"""
    id: str
    intelligence_id: str
    summary: Optional[str] = None
    cheat_scenario: Optional[str] = None
    malicious_pattern: Optional[str] = None
    tech_chain: Optional[str] = None
    risk_score: Optional[int] = None
    recommendations: Optional[str] = None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class IntelligenceItemResponse(BaseModel):
    """情报条目响应"""
    id: str
    source_type: str
    source_name: str
    raw_content: str
    cleaned_content: Optional[str] = None
    content_hash: Optional[str] = None
    risk_level: Optional[str] = None
    risk_category: Optional[str] = None
    status: str
    is_duplicate: bool
    duplicate_of_id: Optional[str] = None
    published_at: Optional[datetime.datetime] = None
    ingested_at: datetime.datetime
    analyzed_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    entities: Optional[List[EntityResponse]] = None
    analysis_report: Optional[AnalysisReportResponse] = None

    model_config = {"from_attributes": True}


class IntelligenceListResponse(BaseModel):
    """分页情报列表响应"""
    items: List[IntelligenceItemResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# Dashboard Schemas
# ============================================================================


class DashboardStatsResponse(BaseModel):
    """仪表盘统计响应"""
    total_items: int = Field(..., description="情报总数")
    risk_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="风险等级分布: {critical: N, high: N, medium: N, low: N}",
    )
    source_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="来源分布: {im: N, group: N, ...}",
    )
    category_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="风险类别分布",
    )
    recent_items: List[IntelligenceItemResponse] = Field(
        default_factory=list,
        description="最近10条情报",
    )
    critical_alerts: int = Field(0, description="严重告警数")
    analyzed_count: int = Field(0, description="已分析数")
    pending_count: int = Field(0, description="待处理数")


# ============================================================================
# Analysis Schemas
# ============================================================================


class AnalyzeRequest(BaseModel):
    """单条分析请求"""
    pass  # 分析单条情报时不需要额外参数


class BatchAnalyzeRequest(BaseModel):
    """批量分析请求"""
    intelligence_ids: List[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="要分析的情报ID列表",
    )
    source_type: Optional[str] = Field(
        None,
        description="按来源类型批量分析（与 intelligence_ids 二选一）",
    )
    risk_level: Optional[str] = Field(
        None,
        description="按风险等级批量分析",
    )


class BatchAnalyzeResponse(BaseModel):
    """批量分析响应"""
    total: int = Field(..., description="总数")
    analyzed: int = Field(..., description="已分析数量")
    skipped: int = Field(..., description="跳过数量（已分析过）")
    errors: List[str] = Field(default_factory=list, description="错误列表")


# ============================================================================
# Ingestion Schemas
# ============================================================================


class IngestRequest(BaseModel):
    """摄入请求"""
    source_types: Optional[List[str]] = Field(
        None,
        description="指定摄入的来源类型，为空则摄入所有来源",
    )
    count: Optional[int] = Field(
        None,
        ge=1,
        le=100,
        description="指定生成数量，为空则使用默认值",
    )


class IngestResponse(BaseModel):
    """摄入响应"""
    total_generated: int = Field(..., description="生成总数")
    new_items: int = Field(..., description="新增数量（去重后）")
    duplicates: int = Field(..., description="重复数量")
    message: str = Field(..., description="结果描述")


# ============================================================================
# Common Schemas
# ============================================================================


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"
    version: str = "1.0.0"
    llm_enabled: bool = False
    database: str = "connected"


class ErrorResponse(BaseModel):
    """通用错误响应"""
    detail: str
    error_code: Optional[str] = None


class DeleteResponse(BaseModel):
    """删除响应"""
    success: bool = True
    message: str