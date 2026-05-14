"""
SQLAlchemy ORM 模型定义

定义三个核心数据表：
- IntelligenceItem: 情报条目
- Entity: 提取的实体
- AnalysisReport: 分析报告
"""

import datetime
import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

from app.database import Base


def generate_uuid() -> str:
    return uuid.uuid4().hex


class IntelligenceItem(Base):
    """情报条目主表"""

    __tablename__ = "intelligence_items"

    id = Column(String(32), primary_key=True, default=generate_uuid)
    source_type = Column(
        String(32),
        nullable=False,
        index=True,
        comment="来源类型: im, group, public_account, forum",
    )
    source_name = Column(
        String(128),
        nullable=False,
        comment="来源名称: 如 Telegram群/微信群/公众号名/论坛板块",
    )
    raw_content = Column(Text, nullable=False, comment="原始情报内容")
    cleaned_content = Column(Text, nullable=True, comment="清洗后的内容")
    content_hash = Column(
        String(64),
        nullable=True,
        index=True,
        comment="内容哈希值，用于去重",
    )
    risk_level = Column(
        String(16),
        nullable=True,
        index=True,
        comment="风险等级: critical, high, medium, low",
    )
    risk_category = Column(
        String(32),
        nullable=True,
        index=True,
        comment="风险类别: account_trading, data_leak, fraud_technique, malware_distribution, phishing, identity_theft, payment_fraud, sim_swapping, captcha_bypass, other",
    )
    status = Column(
        String(16),
        nullable=False,
        default="pending",
        index=True,
        comment="状态: pending, analyzed, archived",
    )
    is_duplicate = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否为重复条目",
    )
    duplicate_of_id = Column(
        String(32),
        nullable=True,
        comment="重复于哪个条目的ID",
    )
    published_at = Column(
        DateTime,
        nullable=True,
        comment="情报发布时间",
    )
    ingested_at = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        comment="系统摄入时间",
    )
    analyzed_at = Column(
        DateTime,
        nullable=True,
        comment="分析完成时间",
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        comment="记录创建时间",
    )

    # 关联关系
    entities = relationship(
        "Entity",
        back_populates="intelligence",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    analysis_report = relationship(
        "AnalysisReport",
        back_populates="intelligence",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )

    # 复合索引
    __table_args__ = (
        Index("ix_intelligence_source_risk", "source_type", "risk_level"),
        Index("ix_intelligence_status_risk", "status", "risk_level"),
        Index("ix_intelligence_ingested_at", "ingested_at"),
    )

    def __repr__(self):
        return f"<IntelligenceItem(id={self.id}, source={self.source_type}, risk={self.risk_level})>"


class Entity(Base):
    """实体提取表"""

    __tablename__ = "entities"

    id = Column(String(32), primary_key=True, default=generate_uuid)
    intelligence_id = Column(
        String(32),
        ForeignKey("intelligence_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_type = Column(
        String(32),
        nullable=False,
        index=True,
        comment="实体类型: slang_term, link, account, tool, phone, email, crypto_address, other",
    )
    entity_value = Column(
        String(512),
        nullable=False,
        comment="实体值",
    )
    entity_context = Column(
        Text,
        nullable=True,
        comment="实体上下文字段",
    )
    confidence = Column(
        Float,
        nullable=False,
        default=0.5,
        comment="置信度 0.0-1.0",
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
    )

    # 关联关系
    intelligence = relationship("IntelligenceItem", back_populates="entities")

    __table_args__ = (
        Index("ix_entity_type_value", "entity_type", "entity_value"),
    )

    def __repr__(self):
        return f"<Entity(type={self.entity_type}, value={self.entity_value})>"


class AnalysisReport(Base):
    """分析报告表"""

    __tablename__ = "analysis_reports"

    id = Column(String(32), primary_key=True, default=generate_uuid)
    intelligence_id = Column(
        String(32),
        ForeignKey("intelligence_items.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    summary = Column(Text, nullable=True, comment="情报摘要")
    cheat_scenario = Column(Text, nullable=True, comment="作弊场景分析")
    malicious_pattern = Column(Text, nullable=True, comment="恶意模式分析")
    tech_chain = Column(Text, nullable=True, comment="技术链条")
    risk_score = Column(
        Integer,
        nullable=True,
        comment="风险评分 0-100",
    )
    recommendations = Column(Text, nullable=True, comment="建议措施")
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
    )

    # 关联关系
    intelligence = relationship("IntelligenceItem", back_populates="analysis_report")

    def __repr__(self):
        return f"<AnalysisReport(intelligence_id={self.intelligence_id}, risk_score={self.risk_score})>"