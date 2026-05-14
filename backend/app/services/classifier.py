"""
风险分类服务

对情报进行风险等级和风险类别判定。
使用全面的关键词词典作为规则引擎降级方案。
"""

import logging
import re
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.intelligence import IntelligenceItem
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class ClassifierService:
    """风险分类服务"""

    # 风险类别定义及对应的关键词
    RISK_CATEGORIES = {
        "account_trading": {
            "name": "账号交易",
            "keywords": [
                "账号", "帐号", "出售", "购买", "批发", "零售", "号商",
                "account", "sell", "buy", "账号交易", "账号库", "扫号",
                "撞库", "credential", "password", "login", "steam",
                "游戏账号", "社交账号", "平台账号", "批量注册",
                "老号", "新号", "白号", "带数据", "cookie",
                "token", "session", "API key", "access",
            ],
            "severity": "high",
        },
        "data_leak": {
            "name": "数据泄露",
            "keywords": [
                "数据", "泄露", "泄漏", "脱库", "数据库", "dump",
                "data", "leak", "breach", "database", "sql",
                "公民信息", "个人信息", "隐私", "身份证", "手机号",
                "邮箱", "地址", "社工库", "查询", "信息贩卖",
                "公民数据", "企业数据", "内部资料", "客户信息",
                "泄漏数据", "打包数据", "一手数据", "数据交换",
            ],
            "severity": "critical",
        },
        "fraud_technique": {
            "name": "欺诈技术",
            "keywords": [
                "诈骗", "欺诈", "骗局", "套路", "话术",
                "fraud", "scam", "phish", "钓鱼",
                "杀猪盘", "杀鱼", "资金盘", "传销", "庞氏",
                "刷单", "返利", "兼职", "套路贷", "裸聊",
                "冒充", "伪装", "伪造", "仿冒", "克隆",
                "引流", "诱导", "套路", "洗脑", "培训",
            ],
            "severity": "high",
        },
        "malware_distribution": {
            "name": "恶意软件分发",
            "keywords": [
                "木马", "病毒", "恶意", "后门", "远控",
                "malware", "trojan", "virus", "backdoor", "rat",
                "免杀", "过杀软", "捆绑", "感染", "传播",
                "勒索", "ransomware", "挖矿", "miner", "botnet",
                "僵尸网络", "payload", "exploit", "shellcode",
                "注入", "hook", "rootkit", "bootkit", "内核",
            ],
            "severity": "critical",
        },
        "phishing": {
            "name": "钓鱼攻击",
            "keywords": [
                "钓鱼", "仿冒", "伪站", "克隆站", "钓鱼站",
                "phishing", "fake", "clone", "spoof",
                "短信钓鱼", "邮件钓鱼", "鱼叉", "水坑",
                "域名", "相似域名", "typosquatting", "homograph",
                "SSL", "证书", "登录页", "验证", "授权",
                "OA", "企业微信", "钉钉", "飞书", "办公",
            ],
            "severity": "high",
        },
        "identity_theft": {
            "name": "身份盗窃",
            "keywords": [
                "身份证", "实名", "认证", "人脸", "活体",
                "identity", "KYC", "verification", "生物识别",
                "四件套", "手持", "照片", "视频", "录像",
                "代认证", "代实名", "过认证", "绕过",
                "企业认证", "对公账户", "个体工商户", "法人",
                "手机卡", "银行卡", "四件", "八件", "全套",
            ],
            "severity": "critical",
        },
        "payment_fraud": {
            "name": "支付欺诈",
            "keywords": [
                "支付", "转账", "收款", "代付", "跑分",
                "payment", "transfer", "money", "launder",
                "洗钱", "资金", "通道", "码商", "承兑",
                "USDT", "加密货币", "虚拟币", "OTC", "场外",
                "支付宝", "微信支付", "银行卡", "四件套",
                "聚合支付", "第四方", "跳转", "支付接口",
            ],
            "severity": "high",
        },
        "sim_swapping": {
            "name": "SIM卡交换",
            "keywords": [
                "SIM", "sim", "手机卡", "补卡", "换卡",
                "sim swap", "sim swapping", "SIM劫持",
                "运营商", "移动", "联通", "电信", "客服",
                "短信验证", "验证码", "SMS", "2FA", "二次验证",
                "拦截", "转发", "嗅探", "伪基站", "IMS",
            ],
            "severity": "critical",
        },
        "captcha_bypass": {
            "name": "验证码绕过",
            "keywords": [
                "验证码", "captcha", "滑块", "点选", "图形验证",
                "打码", "识别", "OCR", "接码", "短信验证码",
                "接码平台", "sms activate", "virtual number",
                "虚拟号", "临时号", "在线接码", "textverified",
                "语音验证", "谷歌验证", "reCAPTCHA", "hcaptcha",
                "自动识别", "AI打码", "机器学习", "深度学习",
            ],
            "severity": "medium",
        },
        "other": {
            "name": "其他",
            "keywords": [
                "代理", "VPN", "IP", "指纹", "浏览器",
                "proxy", "fingerprint", "anti-detect",
                "群控", "云控", "批量", "自动化", "脚本",
                "黑产", "灰产", "地下", "暗网", "暗号",
                "工具", "软件", "插件", "教程", "培训",
            ],
            "severity": "medium",
        },
    }

    # 风险等级关键词（不区分类别）
    CRITICAL_KEYWORDS = [
        "勒索", "ransomware", "数据泄露", "脱库", "0day",
        "zero-day", "公民信息", "大规模", "国家级", "APT",
        "漏洞", "cve", "远程代码执行", "RCE", "提权",
        "数据库", "dump", "社工库", "社工", "爆破",
    ]

    HIGH_KEYWORDS = [
        "木马", "trojan", "钓鱼", "phishing", "诈骗",
        "fraud", "洗钱", "跑分", "账号交易", "批量",
        "后门", "backdoor", "恶意", "malware", "病毒",
    ]

    MEDIUM_KEYWORDS = [
        "代理", "VPN", "工具", "脚本", "自动化",
        "群控", "接码", "captcha", "验证码",
    ]

    LOW_KEYWORDS = [
        "讨论", "咨询", "询问", "学习", "了解",
        "技术分享", "教程", "科普",
    ]

    @staticmethod
    def classify_risk_rule(
        content: str,
    ) -> Tuple[Optional[str], Optional[str], int]:
        """
        基于规则的分类

        使用关键词词典进行风险等级和风险类别判定。

        Returns:
            (risk_level, risk_category, confidence)
        """
        if not content:
            return None, None, 0

        content_lower = content.lower()

        # 第一步：确定风险类别
        category_scores = {}
        for cat_key, cat_info in ClassifierService.RISK_CATEGORIES.items():
            score = 0
            for kw in cat_info["keywords"]:
                kw_lower = kw.lower()
                # 使用正则匹配完整词
                count = len(re.findall(re.escape(kw_lower), content_lower))
                if count > 0:
                    # 关键词越长，权重越高
                    score += count * (len(kw) / 4)
            category_scores[cat_key] = score

        # 选择得分最高的类别
        best_category = max(category_scores, key=category_scores.get)
        best_cat_score = category_scores[best_category]

        if best_cat_score < 1.0:
            best_category = "other"
            best_cat_score = 1.0

        # 第二步：确定风险等级
        risk_scores = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for kw in ClassifierService.CRITICAL_KEYWORDS:
            risk_scores["critical"] += len(re.findall(re.escape(kw.lower()), content_lower))

        for kw in ClassifierService.HIGH_KEYWORDS:
            risk_scores["high"] += len(re.findall(re.escape(kw.lower()), content_lower))

        for kw in ClassifierService.MEDIUM_KEYWORDS:
            risk_scores["medium"] += len(re.findall(re.escape(kw.lower()), content_lower))

        for kw in ClassifierService.LOW_KEYWORDS:
            risk_scores["low"] += len(re.findall(re.escape(kw.lower()), content_lower))

        # 如果内容长度很短且没有任何关键词命中，标记为 low
        has_any_hit = any(v > 0 for v in risk_scores.values())
        if not has_any_hit:
            if len(content) < 20:
                risk_level = "low"
            elif len(content) < 100:
                risk_level = "medium"
            else:
                risk_level = "medium"
        else:
            # 加权计算
            weighted = {
                "critical": risk_scores["critical"] * 5,
                "high": risk_scores["high"] * 3,
                "medium": risk_scores["medium"] * 2,
                "low": risk_scores["low"] * 1,
            }
            risk_level = max(weighted, key=weighted.get)
            if weighted[risk_level] < 1.0:
                risk_level = "low"

        # 综合置信度
        confidence = min(0.95, best_cat_score / (best_cat_score + 2.0))

        return risk_level, best_category, round(confidence, 2)

    async def classify_risk_llm(
        self, content: str
    ) -> Optional[dict]:
        """使用 LLM 进行风险分类"""
        if not llm_service.enabled:
            return None

        categories_list = "\n".join([
            f"- {k}: {v['name']} (严重度: {v['severity']})"
            for k, v in self.RISK_CATEGORIES.items()
        ])

        schema = {
            "risk_level": "critical/high/medium/low",
            "risk_category": "account_trading/data_leak/fraud_technique/malware_distribution/phishing/identity_theft/payment_fraud/sim_swapping/captcha_bypass/other",
            "reasoning": "分类理由的简要说明",
            "key_indicators": ["关键指标1", "关键指标2"],
        }

        result = await llm_service.structured_output(
            system_prompt=(
                "你是一个黑灰产情报分析专家。请对以下情报内容进行风险分类。\n\n"
                f"风险类别定义：\n{categories_list}\n\n"
                "风险等级定义：\n"
                "- critical: 大规模数据泄露、0day漏洞、国家级威胁、勒索软件、APT攻击\n"
                "- high: 账号交易、钓鱼攻击、支付欺诈、木马分发、身份盗窃\n"
                "- medium: 验证码绕过、代理工具、群控软件、一般灰产\n"
                "- low: 技术讨论、资讯分享、低风险内容\n\n"
                "请基于内容客观判断，不要过度升级风险等级。"
            ),
            user_prompt=f"请对以下情报进行风险分类：\n\n{content}",
            output_schema=schema,
            temperature=0.1,
        )

        if result:
            return {
                "risk_level": result.get("risk_level", "medium"),
                "risk_category": result.get("risk_category", "other"),
                "reasoning": result.get("reasoning", ""),
                "key_indicators": result.get("key_indicators", []),
            }

        return None

    async def classify(
        self,
        db: AsyncSession,
        item: IntelligenceItem,
    ) -> Tuple[str, str]:
        """
        对单条情报进行风险分类

        优先使用 LLM，不可用时回退到规则引擎。
        分类结果会保存到数据库。

        Returns:
            (risk_level, risk_category)
        """
        content = item.cleaned_content or item.raw_content

        # 尝试 LLM 分类
        llm_result = await self.classify_risk_llm(content)

        if llm_result:
            risk_level = llm_result["risk_level"]
            risk_category = llm_result["risk_category"]
            logger.debug(
                f"LLM分类: level={risk_level}, category={risk_category}, "
                f"reasoning={llm_result.get('reasoning', '')[:100]}"
            )
        else:
            # 回退到规则引擎
            risk_level, risk_category, confidence = self.classify_risk_rule(content)
            logger.debug(
                f"规则分类: level={risk_level}, category={risk_category}, "
                f"confidence={confidence}"
            )

        # 保存分类结果
        item.risk_level = risk_level
        item.risk_category = risk_category
        await db.flush()

        return risk_level, risk_category


# 全局单例
classifier_service = ClassifierService()