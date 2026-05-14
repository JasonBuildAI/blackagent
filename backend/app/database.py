"""
异步数据库配置

使用 SQLAlchemy 异步引擎 + aiosqlite 实现零配置数据库。
可通过修改 DATABASE_URL 轻松切换至 MySQL/PostgreSQL。
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# 创建异步引擎，echo=False 关闭 SQL 日志
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

# 异步会话工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """所有 ORM 模型的基类"""
    pass


async def get_db() -> AsyncSession:
    """FastAPI 依赖注入：获取数据库会话"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库：创建所有表"""
    async with engine.begin() as conn:
        # 导入所有模型以确保它们被注册
        from app.models.intelligence import IntelligenceItem, Entity, AnalysisReport  # noqa: F401
        from app.models.settings import SystemSetting  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()