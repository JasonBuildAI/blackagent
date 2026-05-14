"""
系统设置模型

存储可在运行时动态修改的配置，如 LLM API Key。
这些设置保存在数据库中，优先级高于环境变量。
"""

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func

from app.database import Base


class SystemSetting(Base):
    """系统设置表"""

    __tablename__ = "system_settings"

    key = Column(String(128), primary_key=True, comment="设置键名")
    value = Column(Text, nullable=True, comment="设置值")
    description = Column(String(512), nullable=True, comment="设置说明")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    def __repr__(self):
        return f"<SystemSetting(key={self.key})>"
