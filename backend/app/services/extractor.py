"""
实体提取服务

从情报内容中自动提取实体：
- 黑话术语
- URL链接
- 账号（QQ/微信/Telegram等）
- 工具/软件
- 电话号码
- 邮箱地址
- 加密货币地址
"""

import logging
import re
from typing import List, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.intelligence import Entity
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class ExtractorService:
    """实体提取服务"""

    # === 正则模式 ===

    # URL 模式
    URL_PATTERN = re.compile(
        r"https?://[^\s<>\"'，。；！？、\n]+|"
        r"[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:/[^\s<>\"'，。；！？、\n]*)?",
        re.IGNORECASE,
    )

    # 邮箱模式
    EMAIL_PATTERN = re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    )

    # 中国大陆手机号（简化匹配）
    PHONE_CN_PATTERN = re.compile(
        r"(?:1[3-9]\d)[\s\-]?\d{4}[\s\-]?\d{4}",
    )

    # QQ号
    QQ_PATTERN = re.compile(
        r"(?:QQ|qq|扣扣)[\s:：]*(\d{5,12})|"
        r"(?<!\d)([1-9]\d{4,11})(?=\s*[，。QQqq扣])",
    )

    # 微信号
    WECHAT_PATTERN = re.compile(
        r"(?:微信|wx|WX|vx|VX|WeChat|wechat)[\s:：]*([a-zA-Z][a-zA-Z0-9_-]{5,19})|"
        r"(?:微信号|WX号)[\s:：]*([a-zA-Z][a-zA-Z0-9_-]{5,19})",
        re.IGNORECASE,
    )

    # Telegram
    TELEGRAM_PATTERN = re.compile(
        r"(?:TG|tg|Telegram|telegram|电报)[\s:：]*@?([a-zA-Z][a-zA-Z0-9_]{4,32})|"
        r"@([a-zA-Z][a-zA-Z0-9_]{4,32})|"
        r"t\.me/([a-zA-Z][a-zA-Z0-9_]{4,32})",
        re.IGNORECASE,
    )

    # Discord
    DISCORD_PATTERN = re.compile(
        r"(?:Discord|discord|DC|dc)[\s:：]*([a-zA-Z0-9_]{2,32}#?\d{0,4})",
        re.IGNORECASE,
    )

    # 加密货币地址
    CRYPTO_PATTERN = re.compile(
        r"(?:0x[a-fA-F0-9]{40})|"  # ETH
        r"(?:[13][a-km-zA-HJ-NP-Z1-9]{25,34})|"  # BTC
        r"(?:T[a-zA-Z0-9]{33})|"  # TRX
        r"(?:0x[a-fA-F0-9]{64})",  # TX Hash
    )

    # === 黑话词典 ===
    SLANG_DICTIONARY = {
        # 交易相关
        "跑分": "利用个人账户为非法资金分流转账的行为",
        "码商": "提供收款二维码帮助洗钱的人",
        "承兑": "USDT等加密货币与法币兑换服务商",
        "料子": "可用于欺诈的个人信息数据",
        "四件套": "身份证+银行卡+手机卡+U盾的组合资料包",
        "八件套": "包含更多个人资料的完整身份包",
        "一手料": "未被使用过的最新泄露数据",
        "二手料": "已被他人使用过的数据",
        "洗料": "对泄露数据进行清洗和验证的过程",
        "通道": "用于资金转移的支付渠道",

        # 账号相关
        "号商": "批量买卖各类平台账号的商人",
        "白号": "刚注册未使用过的新账号",
        "老号": "注册时间较早、有使用痕迹的账号",
        "扫号": "批量检测账号是否存活的工具",
        "撞库": "利用已知密码尝试登录其他平台的攻击",
        "cookie": "浏览器身份凭证，可用于劫持会话",
        "token": "API或应用的身份验证令牌",
        "出号": "出售账号",

        # 攻击工具
        "远控": "远程控制木马",
        "免杀": "绕过杀毒软件检测的技术",
        "壳": "对恶意代码的加密或混淆保护",
        "抓鸡": "控制他人计算机（肉鸡）",
        "肉鸡": "被黑客控制的计算机",
        "DDOS": "分布式拒绝服务攻击",
        "CC攻击": "针对Web应用的拒绝服务攻击",
        "webshell": "网站后门脚本",

        # 黑产链路
        "引流": "将用户引导至特定平台或群组",
        "杀猪盘": "长期培养感情后诱导投资的诈骗",
        "杀鱼": "针对小额的快速诈骗",
        "资金盘": "以投资为名的庞氏骗局",
        "盘口": "赌博网站或诈骗平台",
        "料商": "出售个人信息的中间商",
        "技术员": "为黑产提供技术支持的开发者",
        "出金": "将非法所得提现或变现",

        # 支付/加密货币
        "U": "USDT（泰达币）的代称",
        "油": "USDT的谐音代称",
        "黑U": "来源不明的USDT",
        "OTC": "场外加密货币交易",
        "混币器": "混淆加密货币交易路径的工具",
        "tumbler": "混币器",

        # 通讯工具
        "纸飞机": "Telegram的俗称",
        "飞机": "Telegram的简称",
        "电报": "Telegram的中文名称",
        "蝙蝠": "Bat Messenger加密通讯软件",
        "土豆": "Potato即时通讯软件",
        "飞机群": "Telegram群组",

        # 黑话
        "上车": "参与某项黑产活动",
        "下车": "退出某项黑产活动",
        "黑吃黑": "黑产人员之间的互相欺骗",
        "茶水费": "中介费或介绍费的黑话",
        "担保": "黑产交易中的第三方担保服务",
        "信誉盘": "有信誉的黑产交易平台",

        # 验证码相关
        "接码": "使用虚拟手机号接收验证码",
        "打码": "自动识别图形验证码",
        "猫池": "批量管理SIM卡的设备",
        "卡商": "批量提供SIM卡用于接码的人",
        "真人打码": "人工识别验证码的服务",
    }

    # 工具/软件关键词
    TOOL_KEYWORDS = [
        "改机工具", "一键新机", "伪装工具", "应用分身", "虚拟定位",
        "群控系统", "云控平台", "脚本精灵", "按键精灵", "触动精灵",
        "自动化脚本", "批量注册机", "短信轰炸机", "呼死你",
        "xposed", "magisk", "frida", "ida pro", "ghidra",
        "charles", "fiddler", "burp suite", "wireshark",
        "nmap", "metasploit", "sqlmap", "hydra", "hashcat",
        "cobalt strike", "mimikatz", "powershell empire",
        "shodan", "zoomeye", "fofa", "censys",
        "selenium", "playwright", "puppeteer",
        "android模拟器", "夜神", "雷电", "逍遥", "mumu",
        "指纹浏览器", "multilogin", "ads power", "bit浏览器",
        "代理IP", "http代理", "socks5", "机场",
        "clash", "v2ray", "shadowsocks", "trojan",
    ]

    @staticmethod
    def extract_context(content: str, value: str, context_chars: int = 50) -> str:
        """提取实体在原文中的上下文"""
        idx = content.find(value)
        if idx == -1:
            return ""
        start = max(0, idx - context_chars)
        end = min(len(content), idx + len(value) + context_chars)
        ctx = content[start:end].strip()
        if start > 0:
            ctx = "..." + ctx
        if end < len(content):
            ctx = ctx + "..."
        return ctx

    @staticmethod
    def extract_urls(content: str) -> List[Dict]:
        """提取URL链接"""
        results = []
        seen = set()
        for match in ExtractorService.URL_PATTERN.finditer(content):
            url = match.group(0).strip()
            # 过滤掉明显不是URL的匹配
            if "." not in url or len(url) < 5:
                continue
            if url not in seen:
                seen.add(url)
                results.append({
                    "type": "link",
                    "value": url,
                    "context": ExtractorService.extract_context(content, url),
                    "confidence": 0.9 if url.startswith("http") else 0.7,
                })
        return results

    @staticmethod
    def extract_emails(content: str) -> List[Dict]:
        """提取邮箱地址"""
        results = []
        seen = set()
        for match in ExtractorService.EMAIL_PATTERN.finditer(content):
            email = match.group(0)
            if email not in seen:
                seen.add(email)
                results.append({
                    "type": "email",
                    "value": email,
                    "context": ExtractorService.extract_context(content, email),
                    "confidence": 0.95,
                })
        return results

    @staticmethod
    def extract_phones(content: str) -> List[Dict]:
        """提取电话号码"""
        results = []
        seen = set()
        for match in ExtractorService.PHONE_CN_PATTERN.finditer(content):
            phone = match.group(0).replace(" ", "").replace("-", "")
            if phone not in seen:
                seen.add(phone)
                results.append({
                    "type": "phone",
                    "value": phone,
                    "context": ExtractorService.extract_context(content, match.group(0)),
                    "confidence": 0.85,
                })
        return results

    @staticmethod
    def extract_accounts(content: str) -> List[Dict]:
        """提取各类账号"""
        results = []
        seen = set()

        # QQ
        for match in ExtractorService.QQ_PATTERN.finditer(content):
            qq = match.group(1) or match.group(2)
            if qq and qq not in seen and 10000 <= int(qq) <= 999999999999:
                seen.add(qq)
                results.append({
                    "type": "account",
                    "value": f"QQ:{qq}",
                    "context": ExtractorService.extract_context(content, match.group(0)),
                    "confidence": 0.8,
                })

        # 微信
        for match in ExtractorService.WECHAT_PATTERN.finditer(content):
            wx = match.group(1) or match.group(2)
            if wx and wx not in seen:
                seen.add(wx)
                results.append({
                    "type": "account",
                    "value": f"微信:{wx}",
                    "context": ExtractorService.extract_context(content, match.group(0)),
                    "confidence": 0.8,
                })

        # Telegram
        for match in ExtractorService.TELEGRAM_PATTERN.finditer(content):
            tg = match.group(1) or match.group(2) or match.group(3)
            if tg and tg not in seen and len(tg) >= 4:
                seen.add(tg)
                results.append({
                    "type": "account",
                    "value": f"Telegram:@{tg}",
                    "context": ExtractorService.extract_context(content, match.group(0)),
                    "confidence": 0.85,
                })

        # Discord
        for match in ExtractorService.DISCORD_PATTERN.finditer(content):
            dc = match.group(1)
            if dc and dc not in seen:
                seen.add(dc)
                results.append({
                    "type": "account",
                    "value": f"Discord:{dc}",
                    "context": ExtractorService.extract_context(content, match.group(0)),
                    "confidence": 0.75,
                })

        return results

    @staticmethod
    def extract_slang(content: str) -> List[Dict]:
        """提取黑话术语"""
        results = []
        seen = set()
        content_lower = content.lower()

        for term, definition in ExtractorService.SLANG_DICTIONARY.items():
            term_lower = term.lower()
            if term_lower in content_lower and term not in seen:
                seen.add(term)
                results.append({
                    "type": "slang_term",
                    "value": term,
                    "context": ExtractorService.extract_context(content, term),
                    "confidence": 0.75 if len(term) >= 3 else 0.6,
                    "definition": definition,
                })

        return results

    @staticmethod
    def extract_tools(content: str) -> List[Dict]:
        """提取工具/软件"""
        results = []
        seen = set()
        content_lower = content.lower()

        for tool in ExtractorService.TOOL_KEYWORDS:
            tool_lower = tool.lower()
            if tool_lower in content_lower and tool not in seen:
                seen.add(tool)
                results.append({
                    "type": "tool",
                    "value": tool,
                    "context": ExtractorService.extract_context(content, tool),
                    "confidence": 0.7,
                })

        return results

    @staticmethod
    def extract_crypto_addresses(content: str) -> List[Dict]:
        """提取加密货币地址"""
        results = []
        seen = set()

        for match in ExtractorService.CRYPTO_PATTERN.finditer(content):
            addr = match.group(0)
            if addr not in seen:
                seen.add(addr)

                # 判断类型
                if addr.startswith("0x") and len(addr) == 42:
                    addr_type = "ETH地址"
                elif addr.startswith("0x") and len(addr) == 66:
                    addr_type = "交易哈希"
                elif addr.startswith("T") and len(addr) == 34:
                    addr_type = "TRX地址"
                else:
                    addr_type = "BTC地址"

                results.append({
                    "type": "crypto_address",
                    "value": f"{addr_type}:{addr}",
                    "context": ExtractorService.extract_context(content, addr),
                    "confidence": 0.9,
                })

        return results

    async def extract_entities_rule(self, content: str) -> List[Dict]:
        """
        基于规则提取所有实体

        Returns:
            实体字典列表
        """
        all_entities = []

        all_entities.extend(self.extract_urls(content))
        all_entities.extend(self.extract_emails(content))
        all_entities.extend(self.extract_phones(content))
        all_entities.extend(self.extract_accounts(content))
        all_entities.extend(self.extract_slang(content))
        all_entities.extend(self.extract_tools(content))
        all_entities.extend(self.extract_crypto_addresses(content))

        return all_entities

    async def extract_entities_llm(self, content: str) -> Optional[List[Dict]]:
        """使用 LLM 提取实体"""
        if not llm_service.enabled:
            return None

        schema = {
            "entities": [
                {
                    "type": "slang_term/link/account/tool/phone/email/crypto_address",
                    "value": "实体值",
                    "context": "在原文中的上下文",
                    "confidence": 0.9,
                }
            ]
        }

        result = await llm_service.structured_output(
            system_prompt=(
                "你是一个情报实体提取专家。请从以下黑灰产情报内容中提取所有关键实体。\n\n"
                "实体类型包括：\n"
                "- slang_term: 黑话术语（如：跑分、料子、四件套等）\n"
                "- link: URL链接\n"
                "- account: 社交账号（QQ号、微信号、Telegram号等）\n"
                "- tool: 工具/软件名称\n"
                "- phone: 电话号码\n"
                "- email: 邮箱地址\n"
                "- crypto_address: 加密货币地址\n\n"
                "请尽量全面提取，confidence 根据实体明确程度取 0.5-1.0。"
            ),
            user_prompt=f"请从以下情报内容中提取所有实体：\n\n{content}",
            output_schema=schema,
            temperature=0.1,
        )

        if result and "entities" in result:
            return result["entities"]

        return None

    async def extract(
        self,
        db: AsyncSession,
        item,
    ) -> List[Entity]:
        """
        提取情报中的所有实体并保存到数据库

        优先使用 LLM，不可用时回退到规则引擎。

        Returns:
            Entity 对象列表
        """
        content = item.cleaned_content or item.raw_content

        # 尝试 LLM 提取
        llm_entities = await self.extract_entities_llm(content)

        if llm_entities:
            entity_dicts = llm_entities
            logger.debug(f"LLM提取实体: {len(entity_dicts)} 个")
        else:
            # 回退到规则引擎
            entity_dicts = await self.extract_entities_rule(content)
            logger.debug(f"规则提取实体: {len(entity_dicts)} 个")

        # 保存到数据库
        db_entities = []
        for e in entity_dicts:
            entity = Entity(
                intelligence_id=item.id,
                entity_type=e.get("type", "other"),
                entity_value=e.get("value", ""),
                entity_context=e.get("context", ""),
                confidence=min(1.0, max(0.1, e.get("confidence", 0.5))),
            )
            db.add(entity)
            db_entities.append(entity)

        await db.flush()
        return db_entities


# 全局单例
extractor_service = ExtractorService()