"""
设置路由

提供系统设置的查询和修改接口。
"""

import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.settings_service import settings_service
from app.services.model_providers import get_providers

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["系统设置"])


class SettingUpdateRequest(BaseModel):
    """设置更新请求"""
    value: str = Field(..., description="设置值")


class SettingResponse(BaseModel):
    """设置响应"""
    key: str
    value: str
    description: str
    updated_at: str | None


class SettingsListResponse(BaseModel):
    """设置列表响应"""
    settings: Dict[str, Dict]


class LLMConfigResponse(BaseModel):
    """LLM 配置响应"""
    api_base: str
    model: str
    enabled: bool


class ProviderModel(BaseModel):
    """模型信息"""
    id: str
    name: str
    description: str


class ProviderInfo(BaseModel):
    """服务商信息"""
    id: str
    name: str
    api_base: str
    description: str
    models: List[ProviderModel]


class ProvidersResponse(BaseModel):
    """服务商列表响应"""
    providers: List[ProviderInfo]


@router.get("", response_model=SettingsListResponse)
async def get_all_settings(db: AsyncSession = Depends(get_db)):
    """获取所有系统设置"""
    settings = await settings_service.get_all_settings(db)
    # 隐藏 API Key 的完整值，只显示前4位
    if "llm_api_key" in settings and settings["llm_api_key"]["value"]:
        key = settings["llm_api_key"]["value"]
        settings["llm_api_key"]["value"] = key[:4] + "*" * (len(key) - 4) if len(key) > 4 else "****"
    return SettingsListResponse(settings=settings)


@router.get("/llm", response_model=LLMConfigResponse)
async def get_llm_config(db: AsyncSession = Depends(get_db)):
    """获取 LLM 配置（不含 API Key）"""
    config = await settings_service.get_llm_config(db)
    return LLMConfigResponse(
        api_base=config["api_base"],
        model=config["model"],
        enabled=config["enabled"],
    )


@router.get("/providers", response_model=ProvidersResponse)
async def get_model_providers():
    """获取所有预置模型服务商列表"""
    providers = get_providers()
    return ProvidersResponse(
        providers=[
            ProviderInfo(
                id=p["id"],
                name=p["name"],
                api_base=p["api_base"],
                description=p["description"],
                models=[ProviderModel(**m) for m in p["models"]],
            )
            for p in providers
        ]
    )


@router.put("/{key}", response_model=SettingResponse)
async def update_setting(
    key: str,
    request: SettingUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """更新设置值"""
    success = await settings_service.update_setting(db, key, request.value)
    if not success:
        raise HTTPException(status_code=500, detail="设置更新失败")

    # 获取更新后的设置
    settings = await settings_service.get_all_settings(db)
    setting_data = settings.get(key, {})

    return SettingResponse(
        key=key,
        value=request.value,
        description=setting_data.get("description", ""),
        updated_at=setting_data.get("updated_at"),
    )


@router.post("/llm/test")
async def test_llm_connection(db: AsyncSession = Depends(get_db)):
    """测试 LLM 连接"""
    from app.services.llm_service import llm_service

    config = await settings_service.get_llm_config(db)

    if not config["enabled"]:
        raise HTTPException(status_code=400, detail="LLM 未启用，请先配置 API Key")

    # 临时更新 LLM 服务配置
    llm_service.enabled = True
    llm_service.api_key = config["api_key"]
    llm_service.api_base = config["api_base"]
    llm_service.model = config["model"]

    # 测试连接
    try:
        result = await llm_service.chat_completion(
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10,
        )
        if result is not None:
            return {"success": True, "message": "LLM 连接测试成功"}
        else:
            return {"success": False, "message": "LLM 连接测试失败，请检查配置"}
    except Exception as e:
        logger.error(f"LLM 测试失败: {e}")
        return {"success": False, "message": f"LLM 连接测试失败: {str(e)}"}
