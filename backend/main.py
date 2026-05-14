"""
黑灰产情报分析Agent - 后端主入口

启动命令:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

环境变量:
    - DATABASE_URL: 数据库连接字符串 (默认: sqlite+aiosqlite:///./blackagent.db)
    - LLM_API_KEY: LLM API密钥 (可选)
    - LLM_API_BASE: LLM API基础URL (默认: https://api.openai.com/v1)
    - LLM_MODEL: LLM模型名称 (默认: gpt-4o-mini)
    - SEED_ON_STARTUP: 启动时是否填充模拟数据 (默认: true)
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db, close_db
from app.config import settings as app_settings
from app.routers import intelligence, analysis, settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("=" * 60)
    logger.info("黑灰产情报分析Agent 启动中...")
    logger.info("=" * 60)

    # 初始化数据库
    await init_db()
    logger.info("数据库初始化完成")

    # 初始化默认设置
    from app.services.settings_service import settings_service
    from app.database import async_session_factory

    async with async_session_factory() as db:
        await settings_service.init_default_settings(db)
        await db.commit()
        logger.info("系统设置初始化完成")

    if app_settings.SEED_ON_STARTUP:
        from app.services.ingestion import ingestion_service
        from app.database import async_session_factory

        async with async_session_factory() as db:
            result = await ingestion_service.ingest_from_mock_sources(
                db=db,
                count=50,
            )
            await db.commit()
            logger.info(
                f"模拟数据填充完成: 生成={result['total_generated']}, "
                f"新增={result['new_items']}, 重复={result['duplicates']}"
            )

    logger.info(f"LLM服务状态: {'已启用' if app_settings.LLM_ENABLED else '未启用 (使用规则引擎)'}")
    logger.info(f"服务地址: http://{app_settings.HOST}:{app_settings.PORT}")
    logger.info("=" * 60)

    yield

    # 关闭时
    logger.info("正在关闭服务...")
    await close_db()
    logger.info("服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="黑灰产情报分析Agent API",
    description="自动化黑灰产情报收集、清洗、分类、实体提取和深度分析系统",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "ok",
        "version": "1.0.0",
        "llm_enabled": app_settings.LLM_ENABLED,
        "database": "connected",
    }


# 注册路由
app.include_router(intelligence.router)
app.include_router(analysis.router)
app.include_router(settings.router)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"全局异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误", "error_code": "INTERNAL_ERROR"},
    )


# 启动入口
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=app_settings.RELOAD,
    )
