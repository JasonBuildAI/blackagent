"""
模型服务商预置配置

预置主流 LLM 服务商的 API Base URL 和最新模型列表。
用户只需选择服务商和模型，填写 API Key 即可使用。
"""

from typing import List, Dict


class ModelProvider:
    """模型服务商"""

    def __init__(self, id: str, name: str, api_base: str, models: List[Dict], description: str = ""):
        self.id = id
        self.name = name
        self.api_base = api_base
        self.models = models
        self.description = description


# 预置服务商配置（2025年最新模型）
MODEL_PROVIDERS: List[ModelProvider] = [
    ModelProvider(
        id="openai",
        name="OpenAI",
        api_base="https://api.openai.com/v1",
        description="OpenAI 官方 API",
        models=[
            {"id": "gpt-4.1", "name": "GPT-4.1", "description": "最新旗舰模型，综合能力最强"},
            {"id": "gpt-4.1-mini", "name": "GPT-4.1 Mini", "description": "高性价比，适合大多数场景"},
            {"id": "gpt-4.1-nano", "name": "GPT-4.1 Nano", "description": "超轻量，速度最快"},
            {"id": "gpt-4o", "name": "GPT-4o", "description": "多模态旗舰模型"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "高性价比多模态模型"},
            {"id": "o3", "name": "o3", "description": "推理模型，适合复杂分析"},
            {"id": "o3-mini", "name": "o3 Mini", "description": "轻量推理模型"},
            {"id": "o4-mini", "name": "o4 Mini", "description": "最新轻量推理模型"},
        ],
    ),
    ModelProvider(
        id="deepseek",
        name="DeepSeek",
        api_base="https://api.deepseek.com/v1",
        description="DeepSeek 官方 API（国产，性价比高）",
        models=[
            {"id": "deepseek-chat-v4", "name": "DeepSeek-V4", "description": "最新对话模型，综合能力强劲"},
            {"id": "deepseek-chat", "name": "DeepSeek-V3", "description": "通用对话模型"},
            {"id": "deepseek-reasoner", "name": "DeepSeek-R1", "description": "推理模型，适合深度分析"},
        ],
    ),
    ModelProvider(
        id="zhipu",
        name="智谱 AI (GLM)",
        api_base="https://open.bigmodel.cn/api/paas/v4",
        description="智谱 AI 官方 API（国产）",
        models=[
            {"id": "glm-5.1", "name": "GLM-5.1", "description": "最新旗舰模型"},
            {"id": "glm-4.5", "name": "GLM-4.5", "description": "高性能模型"},
            {"id": "glm-4-flash", "name": "GLM-4-Flash", "description": "极速响应模型"},
            {"id": "glm-4-air", "name": "GLM-4-Air", "description": "高性价比模型"},
            {"id": "glm-4-long", "name": "GLM-4-Long", "description": "长文本模型"},
        ],
    ),
    ModelProvider(
        id="moonshot",
        name="Moonshot (Kimi)",
        api_base="https://api.moonshot.cn/v1",
        description="Moonshot Kimi API（国产，长文本支持）",
        models=[
            {"id": "kimi-k2.5", "name": "Kimi K2.5", "description": "最新旗舰模型，超长上下文"},
            {"id": "kimi-k2", "name": "Kimi K2", "description": "高性能模型"},
            {"id": "kimi-k1.5", "name": "Kimi K1.5", "description": "高性价比模型"},
        ],
    ),
    ModelProvider(
        id="qwen",
        name="通义千问 (Qwen)",
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="阿里云通义千问 API（国产）",
        models=[
            {"id": "qwen3-235b-a22b", "name": "Qwen3-235B", "description": "最新旗舰模型"},
            {"id": "qwen-max", "name": "Qwen-Max", "description": "高性能模型"},
            {"id": "qwen-plus", "name": "Qwen-Plus", "description": "高性价比模型"},
            {"id": "qwen-turbo", "name": "Qwen-Turbo", "description": "极速响应模型"},
        ],
    ),
    ModelProvider(
        id="doubao",
        name="豆包 (Doubao)",
        api_base="https://ark.cn-beijing.volces.com/api/v3",
        description="字节跳动豆包 API（国产）",
        models=[
            {"id": "doubao-pro-256k", "name": "Doubao-Pro-256k", "description": "专业版，超长上下文"},
            {"id": "doubao-pro-128k", "name": "Doubao-Pro-128k", "description": "专业版，长上下文"},
            {"id": "doubao-lite-128k", "name": "Doubao-Lite-128k", "description": "轻量版，高性价比"},
        ],
    ),
    ModelProvider(
        id="siliconflow",
        name="SiliconFlow",
        api_base="https://api.siliconflow.cn/v1",
        description="SiliconFlow 聚合平台（多模型，性价比高）",
        models=[
            {"id": "deepseek-ai/DeepSeek-V3", "name": "DeepSeek-V3", "description": "DeepSeek V3"},
            {"id": "deepseek-ai/DeepSeek-R1", "name": "DeepSeek-R1", "description": "DeepSeek R1 推理"},
            {"id": "Qwen/Qwen2.5-72B-Instruct", "name": "Qwen2.5-72B", "description": "通义千问 72B"},
            {"id": "THUDM/glm-4-9b-chat", "name": "GLM-4-9B", "description": "智谱 GLM-4"},
        ],
    ),
    ModelProvider(
        id="custom",
        name="自定义",
        api_base="",
        description="自定义 OpenAI 兼容 API",
        models=[
            {"id": "", "name": "自定义模型", "description": "手动输入模型名称"},
        ],
    ),
]


def get_providers() -> List[Dict]:
    """获取所有服务商列表（不含详细模型列表）"""
    return [
        {
            "id": p.id,
            "name": p.name,
            "api_base": p.api_base,
            "description": p.description,
            "models": p.models,
        }
        for p in MODEL_PROVIDERS
    ]


def get_provider(provider_id: str) -> ModelProvider | None:
    """获取指定服务商"""
    for p in MODEL_PROVIDERS:
        if p.id == provider_id:
            return p
    return None
