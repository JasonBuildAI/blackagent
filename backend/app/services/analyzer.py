"""
分析引擎服务

对情报进行综合深度分析，生成：
- 摘要（summary）
- 作弊场景（cheat_scenario）
- 恶意模式（malicious_pattern）
- 技术链条（tech_chain）
- 风险评分（risk_score）
- 建议措施（recommendations）
"""

import datetime
import logging
import re
from typing import Optional, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.intelligence import IntelligenceItem, AnalysisReport, Entity
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class AnalyzerService:
    """分析引擎服务"""

    # 作弊场景模式关键词
    CHEAT_SCENARIOS = {
        "批量注册/养号": [
            "批量注册", "自动注册", "注册机", "养号", "批量", "群控",
            "模拟器", "多开", "分身", "改机", "一键新机",
        ],
        "数据泄露/倒卖": [
            "数据", "泄露", "脱库", "数据库", "dump", "公民信息",
            "社工库", "贩卖", "出售数据", "个人信息", "打包",
        ],
        "支付欺诈/洗钱": [
            "洗钱", "跑分", "支付", "转账", "代付", "码商",
            "USDT", "加密货币", "OTC", "资金", "通道",
        ],
        "钓鱼/社会工程学": [
            "钓鱼", "仿冒", "伪站", "冒充", "社工", "诱导",
            "短信", "邮件", "域名", "登录页",
        ],
        "恶意软件分发": [
            "木马", "病毒", "恶意", "后门", "远控", "免杀",
            "捆绑", "勒索", "挖矿", "payload",
        ],
        "身份伪造/冒用": [
            "身份证", "实名", "人脸", "KYC", "四件套", "手持",
            "代认证", "过认证", "企业认证",
        ],
        "验证码绕过": [
            "验证码", "captcha", "接码", "打码", "滑块", "识别",
            "短信验证", "猫池", "语音验证",
        ],
        "账号交易/接管": [
            "账号", "出售", "购买", "cookie", "token", "session",
            "撞库", "扫号", "密码", "登录",
        ],
    }

    # 恶意模式关键词
    MALICIOUS_PATTERNS = {
        "规模化/产业化运营": [
            "批量", "批发", "零售", "产业链", "上下游", "工厂",
            "自动化", "平台", "系统", "招代理", "招商",
        ],
        "技术服务化": [
            "SaaS", "平台", "API", "服务", "出租", "订阅",
            "更新", "维护", "定制", "开发",
        ],
        "跨境/匿名化": [
            "跨境", "海外", "国外", "匿名", "VPN", "代理",
            "加密货币", "比特币", "USDT", "暗网", "Tor",
        ],
        "分工协作": [
            "上家", "下家", "代理", "中介", "担保", "茶水费",
            "接单", "发货", "售后", "培训",
        ],
        "对抗/反检测": [
            "免杀", "过检测", "绕过", "防封", "防检测", "反爬",
            "代理IP", "指纹", "伪装", "模拟",
        ],
    }

    # 技术链条关键词
    TECH_CHAINS = {
        "信息收集": [
            "爬虫", "采集", "收集", "抓取", "扫描", "探测",
            "社工", "查询", "搜索", "shodan", "fofa",
        ],
        "漏洞利用": [
            "漏洞", "exploit", "poc", "exp", "RCE", "注入",
            "XSS", "SQL注入", "命令执行", "上传", "绕过",
        ],
        "权限维持": [
            "后门", "webshell", "远控", "持久化", "计划任务",
            "服务", "自启动", "rootkit", "bootkit",
        ],
        "横向移动": [
            "内网", "横向", "域", "密码", "hash", "pass",
            "mimikatz", "psexec", "wmi", "smb",
        ],
        "数据窃取": [
            "导出", "下载", "打包", "传输", "外传", "exfiltrate",
            "上传", "云盘", "网盘", "ftp",
        ],
        "变现/洗钱": [
            "变现", "出售", "洗钱", "跑分", "USDT", "OTC",
            "混币", "tumbler", "交易所", "承兑",
        ],
    }

    @staticmethod
    def generate_summary_rule(
        content: str,
        risk_level: Optional[str],
        risk_category: Optional[str],
        entities: list,
    ) -> str:
        """基于规则生成摘要"""
        parts = []

        # 风险等级
        level_map = {
            "critical": "【严重威胁】",
            "high": "【高度风险】",
            "medium": "【中等风险】",
            "low": "【低风险】",
        }
        if risk_level:
            parts.append(level_map.get(risk_level, "【未知风险】"))

        # 类别
        category_map = {
            "account_trading": "涉及账号交易活动",
            "data_leak": "涉及数据泄露",
            "fraud_technique": "涉及欺诈技术",
            "malware_distribution": "涉及恶意软件分发",
            "phishing": "涉及钓鱼攻击",
            "identity_theft": "涉及身份盗窃",
            "payment_fraud": "涉及支付欺诈",
            "sim_swapping": "涉及SIM卡交换攻击",
            "captcha_bypass": "涉及验证码绕过",
            "other": "涉及其他灰产活动",
        }
        if risk_category:
            parts.append(category_map.get(risk_category, "涉及异常活动"))

        # 实体信息
        if entities:
            entity_types = set(e.entity_type if hasattr(e, 'entity_type') else e.get('entity_type', '') for e in entities)
            if "account" in entity_types:
                parts.append("涉及可疑账号")
            if "link" in entity_types:
                parts.append("包含可疑链接")
            if "phone" in entity_types:
                parts.append("包含电话号码")
            if "email" in entity_types:
                parts.append("包含邮箱地址")

        # 内容摘要
        if content:
            short = content[:200].replace("\n", " ")
            parts.append(f"内容摘要: {short}...")

        return " | ".join(parts) if parts else "无法生成摘要"

    @staticmethod
    def analyze_cheat_scenario_rule(content: str) -> str:
        """基于规则分析作弊场景"""
        content_lower = content.lower()
        matched = []

        for scenario, keywords in AnalyzerService.CHEAT_SCENARIOS.items():
            score = 0
            for kw in keywords:
                if kw.lower() in content_lower:
                    score += 1
            if score >= 2:
                matched.append((scenario, score))

        if not matched:
            return "未识别出明确的作弊场景，建议人工研判。内容中可能包含一般性灰产讨论或信息分享。"

        matched.sort(key=lambda x: x[1], reverse=True)
        result_parts = []

        for scenario, score in matched[:3]:
            if scenario == "批量注册/养号":
                result_parts.append(
                    "【批量注册/养号】通过自动化工具批量注册平台账号并进行养号操作，"
                    "目的是获取大量可用账号用于后续欺诈、刷量、水军等活动。"
                )
            elif scenario == "数据泄露/倒卖":
                result_parts.append(
                    "【数据泄露/倒卖】涉及公民个人信息或企业数据的非法获取和交易，"
                    "可能通过数据库脱库、内鬼泄露、API滥用等方式获取数据源，再通过暗网或社交平台进行贩卖。"
                )
            elif scenario == "支付欺诈/洗钱":
                result_parts.append(
                    "【支付欺诈/洗钱】利用跑分平台、虚拟货币、第三方支付通道等方式"
                    "进行非法资金的转移和洗白，通常涉及多层账户跳转以规避风控。"
                )
            elif scenario == "钓鱼/社会工程学":
                result_parts.append(
                    "【钓鱼/社会工程学】通过仿冒网站、欺骗性短信/邮件、社交工程手段"
                    "诱导受害者泄露账号密码、个人信息或执行恶意操作。"
                )
            elif scenario == "恶意软件分发":
                result_parts.append(
                    "【恶意软件分发】传播木马、病毒、勒索软件等恶意程序，"
                    "可能通过捆绑正常软件、钓鱼链接、漏洞利用等方式进行投递。"
                )
            elif scenario == "身份伪造/冒用":
                result_parts.append(
                    "【身份伪造/冒用】通过购买或伪造身份证件、人脸视频等资料，"
                    "绕过平台的实名认证和KYC审核，用于注册违规账号或进行欺诈活动。"
                )
            elif scenario == "验证码绕过":
                result_parts.append(
                    "【验证码绕过】利用接码平台、打码服务等绕过短信验证码和图形验证码保护，"
                    "实现批量注册、批量登录等自动化操作。"
                )
            elif scenario == "账号交易/接管":
                result_parts.append(
                    "【账号交易/接管】通过撞库、cookie劫持、token窃取等手段获取他人账号控制权，"
                    "或将非法获取的账号批量出售给下游黑产。"
                )

        return "\n\n".join(result_parts)

    @staticmethod
    def analyze_malicious_pattern_rule(content: str) -> str:
        """基于规则分析恶意模式"""
        content_lower = content.lower()
        matched = []

        for pattern, keywords in AnalyzerService.MALICIOUS_PATTERNS.items():
            score = 0
            for kw in keywords:
                if kw.lower() in content_lower:
                    score += 1
            if score >= 1:
                matched.append((pattern, score))

        if not matched:
            return "未识别出明显的恶意行为模式，可能为零散个体行为或低威胁信息。"

        matched.sort(key=lambda x: x[1], reverse=True)
        result_parts = []

        for pattern, score in matched[:3]:
            if pattern == "规模化/产业化运营":
                result_parts.append(
                    "【规模化/产业化运营】该活动表现出明显的规模化和产业化特征，"
                    "涉及上下游供应链、批量操作、平台化管理等，表明背后有组织的黑产团伙运营。"
                )
            elif pattern == "技术服务化":
                result_parts.append(
                    "【技术服务化】黑产活动呈现SaaS化趋势，提供API接口、订阅制服务、"
                    "定制化开发等，降低了黑产参与门槛，加速了灰黑产业的扩张。"
                )
            elif pattern == "跨境/匿名化":
                result_parts.append(
                    "【跨境/匿名化】活动涉及跨境操作并使用匿名化技术（VPN/代理/加密货币），"
                    "增加了追踪和打击难度，可能涉及跨国黑产组织。"
                )
            elif pattern == "分工协作":
                result_parts.append(
                    "【分工协作】黑产链条呈现高度分工，从信息收集、技术支撑到变现洗钱各环节"
                    "分工明确，通过担保、中介等机制保障交易安全。"
                )
            elif pattern == "对抗/反检测":
                result_parts.append(
                    "【对抗/反检测】使用了多种对抗检测的技术手段，表明攻击者具有较强的安全意识"
                    "和技术能力，对平台风控体系构成严重挑战。"
                )

        return "\n\n".join(result_parts)

    @staticmethod
    def analyze_tech_chain_rule(content: str) -> str:
        """基于规则分析技术链条"""
        content_lower = content.lower()
        matched = []

        for chain, keywords in AnalyzerService.TECH_CHAINS.items():
            score = 0
            for kw in keywords:
                if kw.lower() in content_lower:
                    score += 1
            if score >= 1:
                matched.append((chain, score))

        if not matched:
            return "未识别出完整的技术链条，内容可能属于信息交流或初步试探阶段。"

        matched.sort(key=lambda x: x[1], reverse=True)
        result_parts = ["【技术链条分析】"]

        chain_order = ["信息收集", "漏洞利用", "权限维持", "横向移动", "数据窃取", "变现/洗钱"]
        chain_descriptions = {
            "信息收集": "攻击者首先进行信息收集，通过爬虫、扫描、社工等手段获取目标信息。",
            "漏洞利用": "利用发现的漏洞进行攻击，获取系统初始访问权限。",
            "权限维持": "在目标系统中植入后门、webshell等，确保持久化访问。",
            "横向移动": "在内网中进行横向渗透，获取更多系统的控制权。",
            "数据窃取": "从目标系统中窃取敏感数据并外传。",
            "变现/洗钱": "将窃取的数据或获取的权限变现，通过加密货币、跑分等方式洗白。",
        }

        for chain in chain_order:
            for m_chain, score in matched:
                if m_chain == chain:
                    result_parts.append(f"\n{chain_descriptions[chain]}")
                    break

        return "\n".join(result_parts)

    @staticmethod
    def calculate_risk_score(
        risk_level: Optional[str],
        risk_category: Optional[str],
        entities: list,
        content: str,
    ) -> int:
        """计算风险评分 0-100"""
        score = 0

        # 风险等级基础分
        level_scores = {
            "critical": 40,
            "high": 30,
            "medium": 20,
            "low": 5,
        }
        score += level_scores.get(risk_level, 10)

        # 风险类别加分
        category_scores = {
            "data_leak": 15,
            "malware_distribution": 15,
            "identity_theft": 12,
            "sim_swapping": 12,
            "payment_fraud": 10,
            "phishing": 10,
            "account_trading": 8,
            "fraud_technique": 8,
            "captcha_bypass": 5,
            "other": 3,
        }
        score += category_scores.get(risk_category, 3)

        # 实体数量加分
        entity_count = len(entities) if entities else 0
        if entity_count >= 5:
            score += 10
        elif entity_count >= 3:
            score += 5
        elif entity_count >= 1:
            score += 2

        # 内容长度（长内容可能包含更多信息）
        content_len = len(content) if content else 0
        if content_len > 500:
            score += 10
        elif content_len > 200:
            score += 5

        # 可疑链接加分
        content_lower = content.lower()
        if re.search(r"https?://", content_lower):
            score += 5

        # 加密货币地址加分
        if re.search(r"0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}", content_lower):
            score += 5

        return min(100, max(0, score))

    @staticmethod
    def generate_recommendations_rule(
        risk_level: Optional[str],
        risk_category: Optional[str],
        cheat_scenario: str,
    ) -> str:
        """基于规则生成建议措施"""
        recommendations = []

        # 通用建议
        recommendations.append("1. 持续监控相关情报来源，建立预警机制。")

        if risk_level == "critical":
            recommendations.append(
                "2. 【紧急】立即启动应急响应流程，通知安全团队和相关业务方。"
            )
            recommendations.append(
                "3. 【紧急】对相关系统进行安全排查，检查是否存在被攻击/泄露的痕迹。"
            )
            recommendations.append(
                "4. 【紧急】如果涉及数据泄露，按照数据安全法规要求进行上报和通知。"
            )
        elif risk_level == "high":
            recommendations.append(
                "2. 【重要】升级相关安全策略，加强对应风险类型的检测和防护。"
            )
            recommendations.append(
                "3. 对相关业务进行风险评估，制定针对性的防范措施。"
            )
        elif risk_level == "medium":
            recommendations.append(
                "2. 将相关情报纳入常规监控范围，关注事态发展趋势。"
            )
            recommendations.append(
                "3. 评估是否需要在业务层面进行预防性调整。"
            )
        else:
            recommendations.append(
                "2. 保持关注，定期评估是否需要升级响应级别。"
            )

        # 按类别细化建议
        if risk_category == "account_trading":
            recommendations.append(
                "N. 加强账号注册和登录环节的风控策略，实施设备指纹和异常行为检测。"
            )
        elif risk_category == "data_leak":
            recommendations.append(
                "N. 排查数据库和API接口的数据访问权限，实施数据防泄漏（DLP）措施。"
            )
        elif risk_category == "malware_distribution":
            recommendations.append(
                "N. 更新恶意软件检测规则，加强终端安全防护和软件供应链安全。"
            )
        elif risk_category == "phishing":
            recommendations.append(
                "N. 对仿冒域名进行监控和处置，开展员工钓鱼邮件安全意识培训。"
            )
        elif risk_category == "identity_theft":
            recommendations.append(
                "N. 升级KYC和人脸识别系统的活体检测能力，增加多因素身份验证。"
            )
        elif risk_category == "payment_fraud":
            recommendations.append(
                "N. 加强支付环节的风控规则，实施交易行为分析和异常交易拦截。"
            )
        elif risk_category == "captcha_bypass":
            recommendations.append(
                "N. 升级验证码系统，引入行为式验证和风险决策引擎。"
            )
        elif risk_category == "sim_swapping":
            recommendations.append(
                "N. 对高风险操作增加额外的身份验证步骤，不单纯依赖短信验证码。"
            )

        # 最后一条通用建议
        recommendations.append(
            f"最后. 建议将本条情报归档至知识库，用于后续关联分析和趋势研判。"
        )

        return "\n".join(recommendations)

    async def analyze_llm(self, item: IntelligenceItem) -> Optional[Dict]:
        """使用 LLM 进行深度分析"""
        if not llm_service.enabled:
            return None

        content = item.cleaned_content or item.raw_content

        # 构建实体信息
        entities_info = ""
        if hasattr(item, 'entities') and item.entities:
            entity_strs = []
            for e in item.entities:
                entity_strs.append(f"- {e.entity_type}: {e.entity_value}")
            entities_info = "\n".join(entity_strs)

        schema = {
            "summary": "200字以内的情报摘要",
            "cheat_scenario": "作弊场景分析，描述可能的黑产应用场景和操作手法",
            "malicious_pattern": "恶意模式分析，识别行为特征和组织模式",
            "tech_chain": "技术链条分析，从信息收集到变现的完整链条",
            "risk_score": 75,
            "recommendations": "具体的防护建议和应对措施",
        }

        user_prompt = f"""请对以下黑灰产情报进行深度分析：

情报内容：
{content}

已提取的实体：
{entities_info if entities_info else "无"}

已知风险信息：
- 风险等级：{item.risk_level or '未判定'}
- 风险类别：{item.risk_category or '未判定'}
- 来源类型：{item.source_type}
- 来源名称：{item.source_name}"""

        result = await llm_service.structured_output(
            system_prompt=(
                "你是一个黑灰产情报深度分析专家。请对情报进行全面分析，识别作弊场景、"
                "恶意行为模式和技术链条，评估风险评分（0-100分），并提供具体的防护建议。\n\n"
                "分析要求：\n"
                "1. 基于内容客观分析，不要无根据猜测\n"
                "2. 风险评分应合理：critical级别内容应在70-100分，high在50-80分，medium在30-60分，low在0-30分\n"
                "3. 建议措施应具体可操作\n"
                "4. 使用中文输出"
            ),
            user_prompt=user_prompt,
            output_schema=schema,
            temperature=0.3,
        )

        return result

    async def analyze(
        self,
        db: AsyncSession,
        item: IntelligenceItem,
    ) -> AnalysisReport:
        """
        对单条情报进行全面分析

        优先使用 LLM，不可用时回退到规则引擎。
        分析结果保存到数据库。

        Returns:
            AnalysisReport 对象
        """
        content = item.cleaned_content or item.raw_content

        # 获取关联实体
        entities_list = list(item.entities) if hasattr(item, 'entities') and item.entities else []

        # 尝试 LLM 分析
        llm_result = await self.analyze_llm(item)

        if llm_result:
            logger.debug("使用LLM分析结果")
            summary = llm_result.get("summary", "")
            cheat_scenario = llm_result.get("cheat_scenario", "")
            malicious_pattern = llm_result.get("malicious_pattern", "")
            tech_chain = llm_result.get("tech_chain", "")
            risk_score = llm_result.get("risk_score", 50)
            recommendations = llm_result.get("recommendations", "")
        else:
            # 回退到规则引擎
            logger.debug("LLM不可用，使用规则引擎进行深度分析")

            summary = self.generate_summary_rule(
                content, item.risk_level, item.risk_category, entities_list
            )
            cheat_scenario = self.analyze_cheat_scenario_rule(content)
            malicious_pattern = self.analyze_malicious_pattern_rule(content)
            tech_chain = self.analyze_tech_chain_rule(content)
            risk_score = self.calculate_risk_score(
                item.risk_level, item.risk_category, entities_list, content
            )
            recommendations = self.generate_recommendations_rule(
                item.risk_level, item.risk_category, cheat_scenario
            )

        # 创建分析报告
        report = AnalysisReport(
            intelligence_id=item.id,
            summary=summary,
            cheat_scenario=cheat_scenario,
            malicious_pattern=malicious_pattern,
            tech_chain=tech_chain,
            risk_score=risk_score,
            recommendations=recommendations,
        )

        db.add(report)

        # 更新情报状态
        item.status = "analyzed"
        item.analyzed_at = datetime.datetime.utcnow()

        await db.flush()

        logger.info(
            f"分析完成: id={item.id}, risk_score={risk_score}, "
            f"level={item.risk_level}"
        )

        return report

    async def batch_analyze(
        self,
        db: AsyncSession,
        item_ids: list,
    ) -> dict:
        """
        批量分析情报

        Returns:
            {"total": N, "analyzed": N, "skipped": N, "errors": [...]}
        """
        from sqlalchemy import select
        from app.models.intelligence import IntelligenceItem

        total = len(item_ids)
        analyzed = 0
        skipped = 0
        errors = []

        for item_id in item_ids:
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

                await self.analyze(db, item)
                analyzed += 1

            except Exception as e:
                errors.append(f"ID={item_id}: {str(e)}")
                logger.error(f"批量分析错误 ID={item_id}: {e}")

        return {
            "total": total,
            "analyzed": analyzed,
            "skipped": skipped,
            "errors": errors,
        }


# 全局单例
analyzer_service = AnalyzerService()