"""
应用配置管理

所有配置通过环境变量读取，提供合理的默认值。
系统在不使用LLM API密钥的情况下也能完整运行。
"""

import os
from typing import Optional


class Settings:
    """应用配置类，支持环境变量覆盖"""

    # --- 数据库 ---
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./blackagent.db",
    )

    # --- LLM API ---
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_API_BASE: str = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # LLM启用开关：只有当API_KEY非空时才会尝试使用LLM
    @property
    def LLM_ENABLED(self) -> bool:
        return bool(self.LLM_API_KEY and self.LLM_API_KEY.strip())

    # --- 服务 ---
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"

    # 种子数据：首次启动是否自动填充模拟数据
    SEED_ON_STARTUP: bool = os.getenv("SEED_ON_STARTUP", "true").lower() == "true"

    # 分页默认值
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # LLM 请求超时（秒）
    LLM_TIMEOUT: int = 60

    # 请求重试配置
    LLM_MAX_RETRIES: int = 3
    LLM_RETRY_BACKOFF: float = 1.5


settings = Settings()