"""
模拟数据生成器

生成逼真（但明确虚构）的黑灰产情报数据，
覆盖所有来源类型和风险类别。
"""

import datetime
import random
from typing import List, Optional, Dict


class MockDataGenerator:
    """模拟数据生成器"""

    # 来源配置
    SOURCES = {
        "im": {
            "names": [
                "Telegram黑产讨论组_Alpha",
                "Telegram数据交易频道",
                "蝙蝠加密群聊_Beta",
                "土豆私密通讯群",
                "Telegram技术交流群",
            ],
            "name_prefix": "TG用户",
        },
        "group": {
            "names": [
                "灰产项目交流群",
                "网络技术分享群",
                "跨境支付讨论群",
                "账号资源对接群",
                "黑客技术研习群",
                "数据资源交换群",
                "黑灰产上下游合作群",
                "验证码互助群",
            ],
            "name_prefix": "群成员",
        },
        "public_account": {
            "names": [
                "网安资讯速递",
                "黑产揭秘频道",
                "安全技术观察",
                "暗网情报站",
                "灰产项目分享",
            ],
            "name_prefix": "运营者",
        },
        "forum": {
            "names": [
                "暗网中文论坛_交易区",
                "黑客技术论坛_工具板块",
                "黑产信息交流社区",
                "匿名技术讨论版",
                "数据交易市场",
            ],
            "name_prefix": "论坛用户",
        },
    }

    @staticmethod
    def random_time(days_back: int = 30) -> datetime.datetime:
        """生成随机时间（过去N天内）"""
        now = datetime.datetime.utcnow()
        delta = datetime.timedelta(
            days=random.randint(0, days_back),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        return now - delta

    @staticmethod
    def random_user(source_type: str) -> str:
        """生成随机用户名"""
        prefixes = ["匿名", "路人", "过客", "幽灵", "影子", "暗影"]
        suffixes = ["001", "007", "X", "Z", "V", "Pro"]
        name = f"{random.choice(prefixes)}_{random.choice(suffixes)}"
        return name

    def _build_items(self) -> List[Dict]:
        """构建所有模拟数据条目"""
        items = []

        # ============================================================================
        # IM 来源 (Telegram/蝙蝠/土豆等即时通讯)
        # ============================================================================

        # --- 数据泄露类 ---
        items.append({
            "source_type": "im",
            "source_name": "Telegram数据交易频道",
            "raw_content": (
                "【数据出售】最新一手料，某电商平台2024年用户数据，包含手机号+收货地址+购买记录，"
                "总量约50万条，已清洗验证。手机号有效率95%以上。\n"
                "价格：1000条/500U，1万条/4000U，量大可谈。\n"
                "样品联系 @databroker_vip\n"
                "担保交易，信誉盘，长期合作。"
            ),
            "published_at": self.random_time(3),
        })

        items.append({
            "source_type": "im",
            "source_name": "Telegram黑产讨论组_Alpha",
            "raw_content": (
                "出某社交平台脱裤数据，2024年11月新鲜出炉，约200W条。\n"
                "字段包括：uid, username, phone, email, password_hash(md5)\n"
                "价格私聊，可走担保。\n"
                "已经有人开始撞库了，速度上车。\n"
                "联系：TG @dbmaster2024"
            ),
            "published_at": self.random_time(5),
        })

        # --- 账号交易类 ---
        items.append({
            "source_type": "im",
            "source_name": "Telegram技术交流群",
            "raw_content": (
                "出售Steam账号，各区老号，带游戏库存，可改邮箱密保。\n"
                "美区/俄区/阿根廷区都有，价格美丽。\n"
                "另出Google Voice美国号码，$3/个，量大优惠。\n"
                "TG联系：@account_shop_vip \n"
                "支持USDT/BTC/ETH付款"
            ),
            "published_at": self.random_time(2),
        })

        items.append({
            "source_type": "im",
            "source_name": "蝙蝠加密群聊_Beta",
            "raw_content": (
                "出各大平台cookie，一手货源，存活率高。\n"
                "支持平台：淘宝/京东/拼多多/抖音/快手\n"
                "cookie带设备指纹，可直接登录无需验证。\n"
                "价格：按平台5-15U/个\n"
                "需要的M我，样品免费测试。"
            ),
            "published_at": self.random_time(1),
        })

        # --- 恶意软件类 ---
        items.append({
            "source_type": "im",
            "source_name": "Telegram黑产讨论组_Alpha",
            "raw_content": (
                "最新远控木马出售，免杀360/火绒/腾讯管家/卡巴斯基。\n"
                "功能：远程桌面、文件管理、键盘记录、摄像头捕获、进程管理、反向代理。\n"
                "月付$200，永久$800，提供更新维护。\n"
                "支持测试，满意再买。\n"
                "联系TG @rat_master_pro"
            ),
            "published_at": self.random_time(4),
        })

        items.append({
            "source_type": "im",
            "source_name": "土豆私密通讯群",
            "raw_content": (
                "出最新勒索病毒源码（Python/C++双版本），可定制logo和勒索说明。\n"
                "使用AES-256+RSA-2048加密，支持自动传播（漏洞利用+SMB）。\n"
                "提供编译服务和技术支持。\n"
                "价格：源码$5000，成品$1000/月\n"
                "渠道：TG @ransomware_dev"
            ),
            "published_at": self.random_time(6),
        })

        # --- 身份盗窃类 ---
        items.append({
            "source_type": "im",
            "source_name": "Telegram数据交易频道",
            "raw_content": (
                "四件套出售：身份证+银行卡+手机卡+U盾，可指定地区。\n"
                "全部一手货源，真人实卡，可过大部分平台实名认证。\n"
                "价格：单套800-1500元（看地区），10套起步有优惠。\n"
                "另外提供手持身份证照片、人脸视频录制服务。\n"
                "联系：@id_shop_cn"
            ),
            "published_at": self.random_time(2),
        })

        items.append({
            "source_type": "im",
            "source_name": "蝙蝠加密群聊_Beta",
            "raw_content": (
                "提供企业支付宝/微信商户号代认证，对公账户代办。\n"
                "个体户营业执照代办+法人配合认证，全套服务。\n"
                "可用于支付接口对接、资金收付。\n"
                "价格面议，走担保。\n"
                "蝙蝠联系：ID_business_auth"
            ),
            "published_at": self.random_time(8),
        })

        # --- 支付欺诈类 ---
        items.append({
            "source_type": "im",
            "source_name": "Telegram黑产讨论组_Alpha",
            "raw_content": (
                "跑分平台招商，日化收益1%-3%，适合个人/团队。\n"
                "支持支付宝/微信/银行卡/USDT多种通道。\n"
                "自动接单系统，无需手动操作，挂机即可赚钱。\n"
                "注册即送100元体验金，提现秒到。\n"
                "平台地址：https://paofen-example.top\n"
                "客服TG @paofen_service"
            ),
            "published_at": self.random_time(1),
        })

        items.append({
            "source_type": "im",
            "source_name": "Telegram技术交流群",
            "raw_content": (
                "USDT承兑商招募，OTC场外交易。\n"
                "按交易额返佣0.5%-2%，日结。\n"
                "要求：有一定资金量（1000U起），熟悉加密货币操作。\n"
                "提供担保，安全可靠。\n"
                "TG群：@usdt_otc_group"
            ),
            "published_at": self.random_time(3),
        })

        # --- 验证码绕过 ---
        items.append({
            "source_type": "im",
            "source_name": "土豆私密通讯群",
            "raw_content": (
                "接码平台推荐：支持全球200+国家手机号，可用于各类App注册验证。\n"
                "中国号码 ¥1/次，美国号码$0.3/次，东南亚号码$0.1/次。\n"
                "支持余额充值，API对接，批量操作。\n"
                "平台：sms-activate.org 邀请码送$5余额。\n"
                "另外出猫池设备，16口/32口可选，支持批量管理SIM卡。"
            ),
            "published_at": self.random_time(7),
        })

        items.append({
            "source_type": "im",
            "source_name": "Telegram数据交易频道",
            "raw_content": (
                "AI打码服务：支持滑块验证码、点选验证码、图形验证码自动识别。\n"
                "识别率：滑块95%+，点选90%+，图形85%+。\n"
                "提供API接口，响应速度<2秒。\n"
                "价格：按次计费 ¥0.01/次，量大更优。\n"
                "支持所有主流平台：淘宝/京东/12306/各大银行\n"
                "联系：@captcha_ai_service"
            ),
            "published_at": self.random_time(5),
        })

        # --- 钓鱼攻击 ---
        items.append({
            "source_type": "im",
            "source_name": "蝙蝠加密群聊_Beta",
            "raw_content": (
                "出最新版企业微信钓鱼页面源码，含OA登录/邮箱登录/审批页面。\n"
                "高仿界面，可过域名检测，支持数据回传。\n"
                "套餐包含：钓鱼页源码+域名+SSL证书+数据接收后台。\n"
                "价格：基础版$300，高级版$800。\n"
                "另可定制其他平台（钉钉/飞书/Office365/Gmail）\n"
                "TG：@phish_kit_factory"
            ),
            "published_at": self.random_time(4),
        })

        # --- SIM交换 ---
        items.append({
            "source_type": "im",
            "source_name": "Telegram黑产讨论组_Alpha",
            "raw_content": (
                "提供手机号定位/短信拦截/通话记录查询服务。\n"
                "需要提供目标手机号，可查询实时位置、短信内容、通话详单。\n"
                "运营商内部渠道，数据准确可靠。\n"
                "价格：定位¥500/次，短信拦截¥200/天，详单¥800/月。\n"
                "联系TG：@spy_service_vip\n"
                "另外提供SIM卡复制/补卡服务，详情私聊。"
            ),
            "published_at": self.random_time(9),
        })

        # ============================================================================
        # 群组来源 (微信群/QQ群)
        # ============================================================================

        items.append({
            "source_type": "group",
            "source_name": "灰产项目交流群",
            "raw_content": (
                "群成员_暗影007:\n"
                "分享一个稳定项目：抖音快手批量注册脚本，自带改机+代理IP池，"
                "可日注册1000+账号，存活率80%以上。\n"
                "配套有一键养号脚本，模拟真人操作（点赞/评论/关注/浏览）。\n"
                "养好的白号可自用可出售，现在市场需求大。\n"
                "有需要的兄弟私我，带教程包教会。"
            ),
            "published_at": self.random_time(1),
        })

        items.append({
            "source_type": "group",
            "source_name": "账号资源对接群",
            "raw_content": (
                "群成员_匿名008:\n"
                "大量出微信号：1年+老号/3年+老号/半年白号/当天新号。\n"
                "带实名/不带实名都有，支持改密保，可登录网页版/PC版。\n"
                "另有企业微信已认证号，可用于营销推广。\n"
                "价格：新号¥15，半年号¥35，1年号¥60，3年号¥120。\n"
                "Q：8823456，备注买号。"
            ),
            "published_at": self.random_time(2),
        })

        items.append({
            "source_type": "group",
            "source_name": "网络技术分享群",
            "raw_content": (
                "群成员_过客V:\n"
                "分享一个0day漏洞利用工具，针对某建站系统CMS最新版。\n"
                "可getshell、提权、批量拿站。已测试成功。\n"
                "工具用法简单，输入目标URL即可自动化攻击。\n"
                "本人只做技术研究，请勿用于非法用途。\n"
                "下载链接：https://github.com/fake-security-research/exploit-tool\n"
                "解压密码：research2024"
            ),
            "published_at": self.random_time(3),
        })

        items.append({
            "source_type": "group",
            "source_name": "跨境支付讨论群",
            "raw_content": (
                "群成员_影子Z:\n"
                "长期收U出U，支持人民币/美金/欧元/港币。\n"
                "汇率按实时币安+0.5%，大额可谈。\n"
                "走担保或熟人可先款，新客户需小额试单。\n"
                "另提供USDT混币服务，清洗交易路径，收费5%。\n"
                "飞机群：@crypto_exchange_group\n"
                "Tron地址：TL7cGzF8kJwP3xRmNq5y6mVhB1sKtDfEaX"
            ),
            "published_at": self.random_time(1),
        })

        items.append({
            "source_type": "group",
            "source_name": "黑客技术研习群",
            "raw_content": (
                "群成员_幽灵Pro:\n"
                "出一套完整的渗透测试工具包，包含：\n"
                "- Nmap扫描脚本（自动发现+漏洞检测）\n"
                "- Metasploit定制模块\n"
                "- SQLMap全自动注入工具\n"
                "- Burp Suite Pro破解版\n"
                "- Cobalt Strike 4.9破解版\n"
                "打包价¥500，永久更新。\n"
                "另外承接网站渗透/漏洞检测/安全评估业务，价格私聊。"
            ),
            "published_at": self.random_time(5),
        })

        items.append({
            "source_type": "group",
            "source_name": "数据资源交换群",
            "raw_content": (
                "群成员_匿名X:\n"
                "互换数据资源，本人有一手求职简历数据约100W条（姓名+手机+邮箱+教育/工作经历），"
                "换电商购物数据或社交平台数据。\n"
                "要求一手未流通过的数据，二手勿扰。\n"
                "数据质量可验样品。\n"
                "联系邮箱：datatrader2024@protonmail.com"
            ),
            "published_at": self.random_time(4),
        })

        items.append({
            "source_type": "group",
            "source_name": "黑灰产上下游合作群",
            "raw_content": (
                "群成员_路人001:\n"
                "团队招技术人员，要求熟悉以下至少两种：\n"
                "1. Android逆向/Hook（Xposed/Frida）\n"
                "2. Web安全（常见漏洞利用/webshell免杀）\n"
                "3. Python/Node.js自动化脚本开发\n"
                "4. 代理IP池/指纹浏览器搭建\n"
                "待遇：底薪+项目分成，远程办公，月入30K-80K。\n"
                "有意私聊详谈，需面试通过后上岗。"
            ),
            "published_at": self.random_time(6),
        })

        items.append({
            "source_type": "group",
            "source_name": "验证码互助群",
            "raw_content": (
                "群成员_暗影001:\n"
                "分享一个真人打码平台，24小时在线，人工识别验证码。\n"
                "支持所有类型验证码：数字/字母/滑块/点选/旋转。\n"
                "价格¥0.02/次，量大可包月。\n"
                "平台地址：https://human-captcha-service.example.com\n"
                "注册送100次免费测试。\n"
                "另外招聘打码工，在家办公，日结¥100-200。"
            ),
            "published_at": self.random_time(2),
        })

        items.append({
            "source_type": "group",
            "source_name": "网络技术分享群",
            "raw_content": (
                "群成员_过客X:\n"
                "分享最新版指纹浏览器破解版，支持多开独立环境，"
                "每个环境独立指纹（Canvas/WebGL/WebRTC/Audio/Font等）。\n"
                "兼容AdsPower/Multilogin的数据格式，可直接导入。\n"
                "配合代理IP使用效果更佳，适合跨境电商/社交媒体多账号管理。\n"
                "下载：https://drive.google.com/fake-link/antidetect-crack\n"
                "仅限学习研究使用！"
            ),
            "published_at": self.random_time(7),
        })

        # --- 欺诈技术 ---
        items.append({
            "source_type": "group",
            "source_name": "灰产项目交流群",
            "raw_content": (
                "群成员_影子007:\n"
                "分享杀猪盘全套话术和引流方案，经过实战验证。\n"
                "包含：搭讪话术/感情培养/投资引导/收网技巧。\n"
                "配套素材：帅哥图片/豪车照片/奢侈品/虚拟定位截图。\n"
                "适合新手入门，一条龙教学。\n"
                "引流渠道：探探/Soul/陌陌/抖音/快手。\n"
                "价格¥2999，包教包会。\n"
                "微信：scam_master_vip （加好友备注学技术）"
            ),
            "published_at": self.random_time(3),
        })

        # ============================================================================
        # 公众号来源
        # ============================================================================

        items.append({
            "source_type": "public_account",
            "source_name": "网安资讯速递",
            "raw_content": (
                "【行业资讯】近期监测到黑灰产市场出现新型银行卡四件套交易模式。\n"
                "与以往不同，此次涉及的材料更加完整，包括：\n"
                "身份证原件/银行卡/银行预留手机卡/U盾/网银密码/预留邮箱。\n"
                "整套售价在3000-8000元不等（按地区和银行等级）。\n"
                "此类材料极有可能被用于电信诈骗收款、洗钱等非法活动。\n"
                "建议各平台加强对异常开户行为的监测，特别是同一IP多次开卡的行为。\n"
                "以上信息仅供参考，不代表本号立场。"
            ),
            "published_at": self.random_time(2),
        })

        items.append({
            "source_type": "public_account",
            "source_name": "黑产揭秘频道",
            "raw_content": (
                "【深度揭秘】暗网某知名数据交易市场最新动态：\n"
                "近日有卖家声称拥有某头部快递公司2024年全年运单数据，涵盖收件人/寄件人姓名、电话、地址信息。\n"
                "数据量声称达数亿条，标价50 BTC。\n"
                "安全研究员分析认为该数据来源可能是内部员工泄露或系统API被滥用。\n"
                "建议相关企业立即排查数据访问日志，加强API接口鉴权和频率限制。\n"
                "关注我们，了解更多黑灰产内幕。"
            ),
            "published_at": self.random_time(1),
        })

        items.append({
            "source_type": "public_account",
            "source_name": "安全技术观察",
            "raw_content": (
                "【技术分析】新型Android木马 DarkRat v3 技术剖析：\n"
                "该木马采用多重免杀技术：代码混淆+动态加载+进程注入。\n"
                "核心功能包括：短信拦截、通讯录窃取、键盘记录、屏幕截图、反向代理。\n"
                "通讯协议使用WebSocket加密传输，C2服务器隐藏在Cloudflare CDN后面。\n"
                "传播途径：伪装成正常APK（VPN工具/清理大师/省电助手）在第三方应用市场分发。\n"
                "目前国内主流杀软对其检出率不足30%。\n"
                "建议用户仅从官方应用商店下载应用，开启Google Play Protect。"
            ),
            "published_at": self.random_time(5),
        })

        items.append({
            "source_type": "public_account",
            "source_name": "暗网情报站",
            "raw_content": (
                "【暗网观察】近期暗网论坛出现大量AI换脸服务广告：\n"
                "服务内容包括：\n"
                "1. 照片换脸：¥50/张，可用于绕过人脸识别\n"
                "2. 视频换脸：¥200/段，可合成指定动作的人脸视频\n"
                "3. 实时换脸：¥500/小时，视频通话中实时换脸\n"
                "4. 定制3D人脸模型：¥2000/套，可对接各类SDK\n"
                "此类技术对KYC人脸验证系统构成直接威胁。\n"
                "建议平台方升级活体检测算法，增加微表情/动作指令等多维度验证。\n"
                "本号将持续关注此技术发展趋势。"
            ),
            "published_at": self.random_time(4),
        })

        items.append({
            "source_type": "public_account",
            "source_name": "灰产项目分享",
            "raw_content": (
                "【项目分享】抖音无人直播带货项目：\n"
                "利用OBS虚拟摄像头+预录制视频，实现7x24小时无人直播。\n"
                "通过直播带货赚取佣金，无需真人出镜，无需口才。\n"
                "配合群控系统可批量操作多个账号，放大收益。\n"
                "需要的工具有：OBS Studio / 直播伴侣破解版 / 代理IP / 虚拟定位。\n"
                "日收益500-2000元，稳定项目。\n"
                "关注本号回复「无人直播」获取详细教程。"
            ),
            "published_at": self.random_time(3),
        })

        items.append({
            "source_type": "public_account",
            "source_name": "网安资讯速递",
            "raw_content": (
                "【预警通报】近日发现针对企业财务人员的精准钓鱼攻击活动。\n"
                "攻击者在获取企业组织架构后，冒充CEO/高管发送邮件或微信消息，"
                "指示财务人员向指定账户转账。\n"
                "攻击特征：\n"
                "- 使用高仿邮箱域名（如ceo@company-co.com vs ceo@company.com）\n"
                "- 了解企业内部流程和人员关系\n"
                "- 制造紧急氛围，催促快速处理\n"
                "已有多家企业因此受损，单笔最高损失超500万元。\n"
                "建议企业建立严格的资金审批流程，大额转账必须电话/当面确认。"
            ),
            "published_at": self.random_time(2),
        })

        items.append({
            "source_type": "public_account",
            "source_name": "安全技术观察",
            "raw_content": (
                "【工具测评】主流接码平台横向对比：\n"
                "1. SMS-Activate：覆盖国家最多（180+），价格中等，API稳定\n"
                "2. TextVerified：美国号码为主，价格较高但质量好\n"
                "3. 5SIM：性价比高，俄罗斯/东南亚号码便宜\n"
                "4. SMSPool：适合批量操作，支持长租号码\n"
                "5. 国内接码平台：价格最低，但稳定性差，容易被封\n"
                "建议根据实际需求选择。批量注册推荐SMS-Activate，长期养号推荐TextVerified。\n"
                "本文仅供安全研究参考，请勿用于非法用途。"
            ),
            "published_at": self.random_time(6),
        })

        items.append({
            "source_type": "public_account",
            "source_name": "暗网情报站",
            "raw_content": (
                "【市场行情】2024年12月黑灰产市场价格参考：\n"
                "- 身份证四件套：¥800-2500/套\n"
                "- 企业支付宝认证号：¥3000-8000/个\n"
                "- 银行卡（一类卡）：¥1000-3000/张\n"
                "- 公民个人信息：¥0.1-2/条（按信息完整度）\n"
                "- DDoS攻击服务：¥100/小时起\n"
                "- Webshell（免杀）：¥200-500/个\n"
                "- 远控木马：¥500-2000/月\n"
                "- 钓鱼页面套餐：¥1000-5000/套\n"
                "以上价格仅供参考，实际价格因市场供需波动。"
            ),
            "published_at": self.random_time(1),
        })

        # ============================================================================
        # 论坛来源
        # ============================================================================

        items.append({
            "source_type": "forum",
            "source_name": "暗网中文论坛_交易区",
            "raw_content": (
                "[出售] 某知名招聘网站2024年简历数据\n"
                "发帖人：匿名者_X\n"
                "时间：2024-12-05\n"
                "---\n"
                "数据量：约80万条\n"
                "字段：姓名、性别、年龄、手机号、邮箱、学历、工作经历、期望薪资\n"
                "来源：内部渠道，一手数据\n"
                "价格：整体打包5 BTC或等值USDT\n"
                "不接受零售，不提供样品（可提供极小量截图证明）\n"
                "交易方式：托管/担保均可\n"
                "联系方式：站内信或Session Messenger\n"
                "Session ID: 05a8f3d9c2e1b7f6a4d3c2b1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3\n"
                "---\n"
                "回帖1: 价格偏高，现在简历数据不值这个价\n"
                "回帖2: 同意楼上，80W条5BTC太贵了，3BTC可以考虑\n"
            ),
            "published_at": self.random_time(5),
        })

        items.append({
            "source_type": "forum",
            "source_name": "黑客技术论坛_工具板块",
            "raw_content": (
                "[分享] Burp Suite Professional 2024.12 最新破解版\n"
                "发帖人：ToolMaster\n"
                "时间：2024-12-08\n"
                "---\n"
                "使用方法：\n"
                "1. 下载压缩包并解压\n"
                "2. 运行loader.jar\n"
                "3. 将生成的license复制到Burp Suite\n"
                "4. 点击Manual Activation完成激活\n"
                "下载地址：https://mega.nz/folder/fake-burpsuite-crack\n"
                "解压密码：burp2024\n"
                "---\n"
                "附赠插件包：\n"
                "- Turbo Intruder\n"
                "- Autorize\n"
                "- Logger++\n"
                "- SQLiPy\n"
                "- J2EEScan\n"
                "---\n"
                "声明：仅供学习研究，请于24小时内删除。\n"
                "回帖1: 感谢分享，已成功激活\n"
                "回帖2: 弱弱问下，这个怎么用？有没有教程？"
            ),
            "published_at": self.random_time(8),
        })

        items.append({
            "source_type": "forum",
            "source_name": "黑产信息交流社区",
            "raw_content": (
                "[经验] 抖音/快手批量养号完整方案\n"
                "发帖人：养号达人\n"
                "时间：2024-12-10\n"
                "---\n"
                "一、环境准备\n"
                "- 手机：推荐红米Note系列（刷机方便）\n"
                "- 系统：需root，安装Magisk+Xposed/LSPosed\n"
                "- 改机模块：Device Faker Pro\n"
                "- 代理：每个账号独立IP（推荐住宅代理）\n\n"
                "二、注册\n"
                "- 使用接码平台接收验证码\n"
                "- 注册后24小时内不做任何操作\n"
                "- 完善头像、昵称、简介（用AI生成）\n\n"
                "三、养号（关键阶段）\n"
                "- 第1-3天：每天浏览30分钟，随机点赞10-20个\n"
                "- 第4-7天：增加评论互动，关注目标领域账号\n"
                "- 第8-15天：发布原创内容（AI生成文案+网图）\n"
                "- 15天后：账号成熟可正常使用\n\n"
                "四、注意事项\n"
                "- 不要频繁切换账号\n"
                "- 每天操作时间要符合真人习惯\n"
                "- 避免集中操作被风控\n"
                "---\n"
                "有更好方案的欢迎交流。"
            ),
            "published_at": self.random_time(10),
        })

        items.append({
            "source_type": "forum",
            "source_name": "匿名技术讨论版",
            "raw_content": (
                "[求助] 如何绕过某App的SSL Pinning？\n"
                "发帖人：ReverseNoob\n"
                "时间：2024-12-12\n"
                "---\n"
                "小弟在做某App的抓包分析，遇到了SSL Pinning，试了以下几种方法都不行：\n"
                "1. JustTrustMe模块 - 无效\n"
                "2. Frida SSL Unpinning脚本 - 无效\n"
                "3. 修改APK移除证书校验 - 签名验证过不了\n"
                "4. Objection - 闪退\n\n"
                "App名称不方便透露，是一个金融类App。\n"
                "求大佬指点，可付费咨询。\n"
                "联系方式：reverse_noob@tutanota.com\n"
                "---\n"
                "回帖1: 用Frida的Interceptor hook OkHttp的CertificatePinner.check\n"
                "回帖2: 可能是自定义的SSL Pinning实现，不是用系统API，要具体分析\n"
                "回帖3: 你把APK发我看看，免费帮你分析"
            ),
            "published_at": self.random_time(12),
        })

        items.append({
            "source_type": "forum",
            "source_name": "暗网中文论坛_交易区",
            "raw_content": (
                "[出售] Web漏洞批量扫描工具（自研）\n"
                "发帖人：BugHunter\n"
                "时间：2024-12-15\n"
                "---\n"
                "功能：\n"
                "- 批量域名/URL导入\n"
                "- SQL注入检测（基于时间盲注+布尔盲注）\n"
                "- XSS检测（反射型+存储型）\n"
                "- 文件上传漏洞检测\n"
                "- 敏感文件扫描（备份文件/配置文件/日志文件）\n"
                "- 后台地址爆破\n"
                "- 自动生成报告\n\n"
                "技术栈：Python + aiohttp异步并发\n"
                "速度：单IP下1000个目标约30分钟\n\n"
                "价格：¥2000永久授权（绑定机器码）\n"
                "支持更新维护\n"
                "联系：站内信或@bughunter_tool\n"
                "---\n"
                "附效果截图：[图片1] [图片2] [图片3]"
            ),
            "published_at": self.random_time(15),
        })

        items.append({
            "source_type": "forum",
            "source_name": "数据交易市场",
            "raw_content": (
                "[求购] 收某游戏平台账号数据\n"
                "发帖人：GameDataBuyer\n"
                "时间：2024-12-17\n"
                "---\n"
                "高价收Steam/Epic/Origin/Uplay等游戏平台账号数据。\n"
                "要求：\n"
                "- 字段至少包含：账号/密码/邮箱/邮箱密码\n"
                "- 账号需有游戏库存（价值$10以上）\n"
                "- 存活率要求60%以上\n"
                "- 数据新鲜度：近3个月内\n\n"
                "价格：按账号价值5%-10%\n"
                "信誉买家，长期合作，量大可预付。\n"
                "联系：game_data_buyer@proton.me\n"
                "TG：@game_account_trader"
            ),
            "published_at": self.random_time(17),
        })

        # --- 更多论坛帖子 ---
        items.append({
            "source_type": "forum",
            "source_name": "黑客技术论坛_工具板块",
            "raw_content": (
                "[教程] 零基础搭建钓鱼网站完整指南\n"
                "发帖人：PhishGuide\n"
                "时间：2024-12-18\n"
                "---\n"
                "前置准备：\n"
                "1. 一台境外VPS（推荐搬瓦工/CloudCone）\n"
                "2. 域名（推荐Namecheap，支持BTC支付）\n"
                "3. SSL证书（免费Let's Encrypt即可）\n\n"
                "步骤：\n"
                "1. 使用HTTrack克隆目标网站\n"
                "2. 修改表单提交地址为你的接收脚本\n"
                "3. 部署到VPS并配置SSL\n"
                "4. 设置域名伪装（使用相似字符，如用小写L替代数字1）\n"
                "5. 配置邮件/短信自动提醒\n\n"
                "进阶技巧：\n"
                "- 使用Cloudflare Workers做反向代理隐藏真实IP\n"
                "- 使用域名前置技术绕过企业防火墙检测\n"
                "- 集成IP黑名单，屏蔽安全公司扫描\n\n"
                "附：我已经封装好了一键部署脚本，需要的私信。"
            ),
            "published_at": self.random_time(18),
        })

        items.append({
            "source_type": "forum",
            "source_name": "黑产信息交流社区",
            "raw_content": (
                "[讨论] AI在灰产中的应用前景\n"
                "发帖人：TechTrend\n"
                "时间：2024-12-20\n"
                "---\n"
                "最近ChatGPT/GPT-4/Claude等AI工具发展很快，聊一下在灰产中的应用：\n\n"
                "1. 文案生成：杀猪盘话术/钓鱼邮件/广告文案，AI写的比人好\n"
                "2. 代码生成：自动化脚本/免杀代码/加解密工具，AI可以大幅提高效率\n"
                "3. 数据分析：泄露数据的清洗/分类/匹配，以前要几天现在几小时\n"
                "4. DeepFake：换脸/变声，绕过KYC和社交工程\n"
                "5. 客服机器人：自动回复客户问题，24小时接单\n\n"
                "AI降低了灰产的技术门槛，以后竞争会更激烈。\n"
                "大家觉得还有什么应用场景？\n"
                "---\n"
                "回帖1: AI打码已经有人在做了，效果比传统OCR好很多\n"
                "回帖2: 语音合成也越来越真，电话诈骗效果很好\n"
                "回帖3: 怕啥，AI防守也在进步，猫鼠游戏罢了"
            ),
            "published_at": self.random_time(20),
        })

        items.append({
            "source_type": "forum",
            "source_name": "匿名技术讨论版",
            "raw_content": (
                "[讨论] 如何安全地变现盗取的加密货币？\n"
                "发帖人：CryptoNoob\n"
                "时间：2024-12-22\n"
                "---\n"
                "手上有一些ETH和ERC-20 token，来源不方便说。\n"
                "想变现成法币，但怕被追踪。\n"
                "考虑过的方案：\n"
                "1. Tornado Cash混币（但被制裁了，使用有风险）\n"
                "2. 跨链桥换成隐私币（XMR/ZEC）再换回来（gas费高）\n"
                "3. OTC场外找承兑商（怕被黑吃黑）\n"
                "4. DeFi流动性池（滑点太大）\n\n"
                "求大佬指点安全的变现路径，可付费咨询。\n"
                "---\n"
                "回帖1: 别用Tornado，OFAC重点监控，用了直接被标记\n"
                "回帖2: 小额多次走DEX，大额分多地址走OTC，别贪便宜找不知名承兑商\n"
                "回帖3: 现在链上分析工具很强大，建议还是不要碰"
            ),
            "published_at": self.random_time(22),
        })

        # --- 更多 IM 数据 ---
        items.append({
            "source_type": "im",
            "source_name": "Telegram数据交易频道",
            "raw_content": (
                "出某银行信用卡申请数据，包含姓名/身份证号/手机号/单位信息/收入水平。\n"
                "数据量约30万条，按地区分类可单独购买。\n"
                "适合精准营销/贷款推广。\n"
                "价格：全国打包15W RMB，分省2W-5W。\n"
                "样品20条免费测试。\n"
                "TG：@bank_data_seller"
            ),
            "published_at": self.random_time(3),
        })

        items.append({
            "source_type": "im",
            "source_name": "蝙蝠加密群聊_Beta",
            "raw_content": (
                "长期出租代理IP池，含50万+全球IP，支持HTTP/SOCKS5。\n"
                "包含住宅IP、机房IP、移动IP，按需选择。\n"
                "可用于爬虫/注册/投票/刷量/游戏/跨境电商等。\n"
                "提供API接口，支持自动切换IP。\n"
                "价格：¥500/月 10万IP，¥2000/月 50万IP。\n"
                "联系蝙蝠：proxy_pool_service"
            ),
            "published_at": self.random_time(1),
        })

        items.append({
            "source_type": "im",
            "source_name": "Telegram黑产讨论组_Alpha",
            "raw_content": (
                "出CC攻击面板，美国/欧洲高防服务器，单发100Gbps+。\n"
                "支持Layer4（SYN/ACK/UDP/ICMP Flood）和Layer7（HTTP Flood）。\n"
                "面板自带流量统计和攻击日志。\n"
                "价格：$50/天，$300/周，$1000/月。\n"
                "可测试，攻击效果保证。\n"
                "TG：@ddos_panel_shop"
            ),
            "published_at": self.random_time(4),
        })

        # --- 更多群组数据 ---
        items.append({
            "source_type": "group",
            "source_name": "网络技术分享群",
            "raw_content": (
                "群成员_暗影X:\n"
                "分享一个短信轰炸机源码（Python版），支持多线程并发。\n"
                "内置200+短信接口，自动轮换，不重复轰炸。\n"
                "支持自定义轰炸频率（1-100条/分钟）和持续时间。\n"
                "已打包成exe，傻瓜式操作。\n"
                "下载：https://disk.example.com/sms-bomber\n"
                "仅供学习socket编程，请勿恶意使用。"
            ),
            "published_at": self.random_time(6),
        })

        items.append({
            "source_type": "group",
            "source_name": "灰产项目交流群",
            "raw_content": (
                "群成员_路人Z:\n"
                "出最新版淘宝/京东自动抢购脚本（秒杀脚本）。\n"
                "支持多账号/多商品同时抢购，毫秒级响应。\n"
                "适配安卓/IOS，无需root/越狱。\n"
                "价格¥299永久，包更新。\n"
                "另外承接代抢服务：茅台/球鞋/手机/门票等，成功率80%+。\n"
                "QQ群：88234567（加群备注抢购）"
            ),
            "published_at": self.random_time(2),
        })

        items.append({
            "source_type": "group",
            "source_name": "跨境支付讨论群",
            "raw_content": (
                "群成员_幽灵Pro:\n"
                "提供PayPal/Stripe/Square等海外支付账户代办服务。\n"
                "资料真实可验证，可用于独立站收款。\n"
                "包含：美国/香港/英国/日本等地公司注册+银行开户+支付账户。\n"
                "全套¥15000起，支持分期。\n"
                "另出售已验证的PayPal/Stripe老号，带流水记录。\n"
                "TG：@payment_accounts_vip"
            ),
            "published_at": self.random_time(8),
        })

        # --- 更多公众号数据 ---
        items.append({
            "source_type": "public_account",
            "source_name": "灰产项目分享",
            "raw_content": (
                "【项目拆解】知乎好物推荐月入过万的方法：\n"
                "利用ChatGPT批量生成高质量回答，挂载好物推荐链接赚取佣金。\n"
                "核心步骤：\n"
                "1. 使用代理IP+指纹浏览器注册多个知乎账号\n"
                "2. 养号7-15天（提升盐值）\n"
                "3. 用爬虫监控热门问题\n"
                "4. AI批量生成+人工微调回答\n"
                "5. 挂载京东/淘宝/拼多多好物链接\n"
                "收益：单账号日均佣金50-200元，10个号就是500-2000元/天。\n"
                "关注回复「知乎」获取详细SOP。"
            ),
            "published_at": self.random_time(5),
        })

        items.append({
            "source_type": "public_account",
            "source_name": "安全技术观察",
            "raw_content": (
                "【技术分析】暗网新型勒索软件 ShadowLock 深度分析：\n"
                "该勒索软件采用Rust编写，特点如下：\n"
                "1. 小巧高效：编译后仅500KB\n"
                "2. 加密快速：使用ChaCha20-Poly1305算法\n"
                "3. 免杀出色：静态/动态检测绕过率>90%\n"
                "4. 传播方式：利用EternalBlue漏洞+Pass-the-Hash横向移动\n"
                "5. 支付方式：仅接受Monero（XMR），增加追踪难度\n\n"
                "感染迹象：\n"
                "- 文件后缀变为.shadow\n"
                "- 桌面壁纸被替换为勒索信息\n"
                "- 每个目录下出现README_SHADOW.txt\n\n"
                "目前无免费解密工具，建议做好数据备份和网络隔离。"
            ),
            "published_at": self.random_time(7),
        })

        items.append({
            "source_type": "public_account",
            "source_name": "暗网情报站",
            "raw_content": (
                "【渠道揭秘】黑灰产从业者的「货源」从哪里来？\n"
                "1. 内鬼泄露：企业内部人员（客服/运维/开发）出售数据\n"
                "2. API漏洞：通过未授权API接口批量爬取\n"
                "3. SQL注入：利用Web漏洞直接拖库\n"
                "4. 社工钓鱼：通过钓鱼邮件/伪基站获取\n"
                "5. 第三方泄露：合作伙伴/供应商泄露\n"
                "6. 公开数据聚合：爬取公开信息进行关联分析\n\n"
                "数据显示，60%以上的数据泄露来自内部人员或API漏洞。\n"
                "建议企业加强内部数据访问控制和API安全审计。"
            ),
            "published_at": self.random_time(10),
        })

        # 继续补充更多条目以达到 50+
        items.append({
            "source_type": "im",
            "source_name": "土豆私密通讯群",
            "raw_content": (
                "出手机远程监控软件（间谍软件），安装后对方无感知。\n"
                "功能：通话录音、短信监控、GPS定位、WhatsApp/微信/TG聊天记录、"
                "摄像头偷拍、麦克风监听、键盘记录。\n"
                "支持安卓/iOS，需要物理接触目标手机5分钟完成安装。\n"
                "价格：安卓版¥500/月，iOS版¥1500/月（需越狱）。\n"
                "包教包会，远程指导。\n"
                "联系：@spy_app_vip"
            ),
            "published_at": self.random_time(11),
        })

        items.append({
            "source_type": "group",
            "source_name": "账号资源对接群",
            "raw_content": (
                "群成员_影子001:\n"
                "出Apple ID各区域老号（美区/日区/港区/国区），带消费记录可退款。\n"
                "可用于App下载/内购/订阅等。\n"
                "美区号$5/个，日区$8/个，港区$10/个，国区¥3/个。\n"
                "另有Apple礼品卡（折扣卡）：美区7折，日区6.5折。\n"
                "Q：6634521，备注苹果号。"
            ),
            "published_at": self.random_time(3),
        })

        items.append({
            "source_type": "forum",
            "source_name": "暗网中文论坛_交易区",
            "raw_content": (
                "[出售] 2024年最新版身份证生成器+人脸合成工具\n"
                "发帖人：ID_Factory\n"
                "时间：2024-12-25\n"
                "---\n"
                "使用AI StyleGAN生成高仿真人脸照片，配合身份证信息生成完整证件。\n"
                "特点：\n"
                "- 人脸真实感强，肉眼难辨\n"
                "- 可指定年龄/性别/地区\n"
                "- 生成的身份证可过大部分OCR识别\n"
                "- 配套人脸视频生成（眨眼/摇头/张嘴动作）\n\n"
                "应用场景：\n"
                "- 绕过平台实名认证\n"
                "- 注册各类账号\n"
                "- KYC验证绕过\n\n"
                "价格：工具¥5000/套，包含训练好的模型文件。\n"
                "---\n"
                "回帖1: 现在KYC都有活体检测，照片没用了吧\n"
                "回帖2: 楼上不知道有视频生成功能吗？眨眼点头都可以模拟"
            ),
            "published_at": self.random_time(25),
        })

        items.append({
            "source_type": "im",
            "source_name": "Telegram技术交流群",
            "raw_content": (
                "出Google/微软/亚马逊云账号（AWS/Azure/GCP）。\n"
                "带$200-$5000试用余额，可用于搭建节点/挖矿/爬虫等。\n"
                "已过电话/信用卡验证，到手即用。\n"
                "价格按余额5%-10%计算。\n"
                "另外出售云服务账号注册教程（含虚拟信用卡渠道）。\n"
                "TG：@cloud_accounts_shop"
            ),
            "published_at": self.random_time(2),
        })

        items.append({
            "source_type": "group",
            "source_name": "黑灰产上下游合作群",
            "raw_content": (
                "群成员_过客Pro:\n"
                "寻找有流量的渠道合作，提供CPA/CPS变现方案。\n"
                "项目：\n"
                "1. 棋牌/彩票/体育博彩推广（CPA ¥50-200/个充值用户）\n"
                "2. 色情直播/约会App推广（CPA ¥10-30/下载）\n"
                "3. 金融理财/贷款推广（CPS 按转化分成20%-50%）\n"
                "4. 游戏私服推广（CPS 充值分成30%-60%）\n"
                "要求：日流量1000+，任何渠道均可（网站/社群/短视频/SEO）。\n"
                "提供推广素材和实时数据后台，日结/周结。\n"
                "联系TG @cpa_affiliate_network"
            ),
            "published_at": self.random_time(5),
        })

        items.append({
            "source_type": "public_account",
            "source_name": "黑产揭秘频道",
            "raw_content": (
                "【行业分析】2024年黑灰产市场规模预估：\n"
                "据不完全统计，国内黑灰产市场规模已突破千亿级别，主要细分领域：\n"
                "- 电信网络诈骗：约400亿\n"
                "- 网络赌博：约300亿\n"
                "- 数据黑市：约150亿\n"
                "- 恶意软件/勒索：约100亿\n"
                "- 虚假流量/刷量：约80亿\n"
                "- 账号交易/接码/打码：约50亿\n\n"
                "产业链高度成熟，从业人员预估超过200万人。\n"
                "AI技术的应用正在加速产业升级，值得警惕。\n"
                "本数据仅供参考，实际规模可能更大。"
            ),
            "published_at": self.random_time(8),
        })

        items.append({
            "source_type": "forum",
            "source_name": "黑客技术论坛_工具板块",
            "raw_content": (
                "[分享] SQLMap Tamper脚本合集（过WAF专用）\n"
                "发帖人：SQLInjectionMaster\n"
                "时间：2024-12-28\n"
                "---\n"
                "整理了30+个绕过WAF的Tamper脚本，兼容最新版SQLMap：\n\n"
                "- space2comment: 空格替换为/**/，绕过基础过滤\n"
                "- space2hash: 空格替换为%23%0A，绕过阿里云WAF\n"
                "- charencode: URL全编码，绕过关键字检测\n"
                "- charunicodeencode: Unicode编码，绕过百度云防护\n"
                "- equaltolike: 等号替换为LIKE\n"
                "- greatest: 绕过比较符号过滤\n"
                "- modsecurityversioned: 绕过ModSecurity\n"
                "- randomcase: 随机大小写\n\n"
                "使用方式：sqlmap -u URL --tamper=脚本名\n"
                "多个tamper可组合使用：--tamper=space2comment,randomcase\n"
                "---\n"
                "下载：https://paste.example.com/sqlmap-tamper-collection"
            ),
            "published_at": self.random_time(28),
        })

        items.append({
            "source_type": "im",
            "source_name": "Telegram数据交易频道",
            "raw_content": (
                "【紧急出售】某省运营商2024年Q4通话详单，数据量约500万条。\n"
                "字段：主叫号码/被叫号码/通话时间/通话时长/基站位置。\n"
                "可用于目标定位、关系分析等。\n"
                "价格：30万RMB整包，不零售。\n"
                "数据来源：内部渠道，保证一手。\n"
                "交易方式：BTC/门罗币，走担保。\n"
                "TG @telecom_data_seller"
            ),
            "published_at": self.random_time(1),
        })

        items.append({
            "source_type": "group",
            "source_name": "数据资源交换群",
            "raw_content": (
                "群成员_暗影Pro:\n"
                "互换数据，本人有：\n"
                "- 某社交App用户关系链数据（A关注B/互为好友等）约2000万条关系\n"
                "- 某电商平台商品评论数据（含用户ID+评论内容+评分）约500万条\n"
                "想换：金融/医疗/政府相关数据，要求一手未流通。\n"
                "有意者私信详谈。"
            ),
            "published_at": self.random_time(7),
        })

        items.append({
            "source_type": "public_account",
            "source_name": "网安资讯速递",
            "raw_content": (
                "【技术前沿】新型浏览器指纹追踪技术解析：\n"
                "传统指纹浏览器主要修改Canvas/WebGL/WebRTC等指纹，"
                "但最新的追踪技术已经扩展到了以下维度：\n"
                "1. AudioContext指纹（音频硬件特征）\n"
                "2. Battery API（电池状态信息）\n"
                "3. 传感器API（加速度计/陀螺仪特征）\n"
                "4. 字体渲染差异\n"
                "5. CSS媒体查询（屏幕尺寸特征）\n"
                "6. 键盘布局检测\n\n"
                "以上特征组合可形成近乎唯一的浏览器指纹。\n"
                "建议安全团队关注此类技术，更新反欺诈策略。\n"
                "个人用户可以使用Tor浏览器或Brave浏览器增强隐私保护。"
            ),
            "published_at": self.random_time(9),
        })

        items.append({
            "source_type": "forum",
            "source_name": "匿名技术讨论版",
            "raw_content": (
                "[教程] 微信/支付宝免密支付漏洞利用方法\n"
                "发帖人：PaymentHacker\n"
                "时间：2024-12-30\n"
                "---\n"
                "发现一个支付逻辑漏洞，利用免密支付+小额双免+延迟清算的特性。\n"
                "原理：\n"
                "1. 使用他人绑定的银行卡开通小额免密支付（需要获取支付密码）\n"
                "2. 在限额内（通常单笔≤1000，日累计≤3000）进行消费\n"
                "3. 利用T+1清算的时间差进行套现\n\n"
                "实操步骤已加密，需要的付费解锁。\n"
                "价格¥299，包教会。\n"
                "联系TG @payment_hack_vip\n"
                "---\n"
                "管理员提醒：此帖涉嫌违法内容，已限制回复。\n"
                "回帖已被禁用。"
            ),
            "published_at": self.random_time(30),
        })

        items.append({
            "source_type": "im",
            "source_name": "蝙蝠加密群聊_Beta",
            "raw_content": (
                "专注各类App拉新/促活/注册任务，长期高价收量。\n"
                "合作方式：\n"
                "1. 提供自动化脚本+代理IP方案，你只需挂机跑量\n"
                "2. 提供指定App的任务清单和价格表\n"
                "3. 按日结算，数据后台实时可查\n\n"
                "适合有设备资源（手机/模拟器）的个人或团队。\n"
                "日均收益¥200-500/台设备。\n"
                "无需任何投入，零风险，操作简单。\n"
                "联系蝙蝠：app_task_network"
            ),
            "published_at": self.random_time(4),
        })

        items.append({
            "source_type": "group",
            "source_name": "灰产项目交流群",
            "raw_content": (
                "群成员_幽灵007:\n"
                "分享一个稳定项目：虚拟币搬砖套利。\n"
                "原理：利用不同交易所之间的价格差异进行套利。\n"
                "已开发自动监控脚本，发现差价>0.5%自动执行买卖。\n"
                "需要的工具：\n"
                "- 币安/OKX/火币等主流交易所账号\n"
                "- 每个交易所预存500-1000U作为流动资金\n"
                "- 自动交易脚本（本人提供）\n\n"
                "风险极低，只要价差存在就能稳定盈利。\n"
                "本人在做，月收益10%-30%。\n"
                "脚本¥2999，包部署。"
            ),
            "published_at": self.random_time(6),
        })

        items.append({
            "source_type": "public_account",
            "source_name": "安全技术观察",
            "raw_content": (
                "【漏洞预警】CVE-2024-XXXXX: 某广泛使用的开源框架远程代码执行漏洞\n"
                "CVSS评分：9.8（严重）\n"
                "影响版本：< 3.2.5\n"
                "漏洞类型：反序列化导致RCE\n"
                "利用条件：无需认证，网络可达即可\n"
                "影响范围：全球约500万+网站使用该框架\n\n"
                "PoC已在GitHub公开，野外利用已开始。\n"
                "修复方案：升级至3.2.5及以上版本，或部署WAF临时防护规则。\n"
                "建议安全团队立即排查受影响资产并尽快修复。\n"
                "关注我们获取最新漏洞情报。"
            ),
            "published_at": self.random_time(2),
        })

        # 添加一些相似的条目用于测试去重
        items.append({
            "source_type": "im",
            "source_name": "Telegram数据交易频道",
            "raw_content": (
                "【数据出售】最新一手料，某电商平台2024年用户数据，包含手机号+收货地址+购买记录，"
                "总量约50万条，已清洗验证。手机号有效率95%以上。\n"
                "价格：1000条/500U，1万条/4000U，量大可谈。\n"
                "样品联系 @databroker_vip\n"
                "担保交易，信誉盘，长期合作。"
            ),
            "published_at": self.random_time(1),
        })

        items.append({
            "source_type": "group",
            "source_name": "账号资源对接群",
            "raw_content": (
                "群成员_匿名008:\n"
                "大量出微信号：1年+老号/3年+老号/半年白号/当天新号。\n"
                "带实名/不带实名都有，支持改密保，可登录网页版/PC版。\n"
                "另有企业微信已认证号，可用于营销推广。\n"
                "价格：新号¥15，半年号¥35，1年号¥60，3年号¥120。\n"
                "Q：8823456，备注买号。"
            ),
            "published_at": self.random_time(1),
        })

        return items

    def generate(
        self,
        source_types: Optional[List[str]] = None,
        count: Optional[int] = None,
    ) -> List[Dict]:
        """
        生成模拟数据

        Args:
            source_types: 指定来源类型，None=全部
            count: 指定数量，None=全部

        Returns:
            模拟数据条目列表
        """
        all_items = self._build_items()

        # 过滤来源类型
        if source_types:
            all_items = [
                item for item in all_items
                if item["source_type"] in source_types
            ]

        # 限制数量
        if count is not None:
            if count > len(all_items):
                # 轮询重复以填充数量
                result = []
                idx = 0
                while len(result) < count:
                    item = all_items[idx % len(all_items)].copy()
                    # 稍微修改时间以避免完全相同的条目
                    item["published_at"] = self.random_time(30)
                    result.append(item)
                    idx += 1
                return result[:count]
            else:
                return random.sample(all_items, count)

        return all_items