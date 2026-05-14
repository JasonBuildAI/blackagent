# 黑灰产情报分析 Agent

自动化黑灰产情报收集、清洗、分类、实体提取和深度分析系统。

## 功能特性

- **多源情报摄入**: 支持 IM聊天群组、公众号、论坛等多源渠道的情报数据
- **智能清洗去重**: 基于规则和 LLM 的内容清洗，自动去重
- **风险分类**: 10+ 风险类别自动分类（数据泄露、账号交易、钓鱼攻击等）
- **实体提取**: 自动提取黑话术语、链接、账号、工具等关键实体
- **深度分析**: 识别作弊场景、恶意模式、技术链条，生成分析报告
- **可视化仪表盘**: 实时展示风险分布、来源统计、告警数量

## 技术架构

### 后端
- FastAPI + SQLAlchemy (异步)
- SQLite (默认，可切换 MySQL/PostgreSQL)
- LLM 集成 (OpenAI 兼容 API，可选)
- 规则引擎降级方案

### 前端
- React + TypeScript
- TailwindCSS
- React Router
- Recharts 图表

## 快速启动

### 环境要求
- Python 3.11+
- Node.js 18+
- npm 或 yarn

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务启动时自动：
- 初始化数据库
- 填充 50 条模拟情报数据

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动前端服务

```bash
cd frontend
npm run dev
```

前端地址: http://localhost:5173

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./blackagent.db` | 数据库连接 |
| `LLM_API_KEY` | 空 | LLM API 密钥（可选） |
| `LLM_API_BASE` | `https://api.openai.com/v1` | LLM API 地址 |
| `LLM_MODEL` | `gpt-4o-mini` | LLM 模型名称 |
| `SEED_ON_STARTUP` | `true` | 启动时填充模拟数据 |
| `HOST` | `0.0.0.0` | 服务绑定地址 |
| `PORT` | `8000` | 服务端口 |

### LLM 配置

系统内置规则引擎，**无需 LLM Key 即可完整运行**。

如需使用 LLM 增强分析能力，可配置：

```bash
# Windows
set LLM_API_KEY=your-api-key
set LLM_API_BASE=https://api.openai.com/v1

# Linux/Mac
export LLM_API_KEY=your-api-key
export LLM_API_BASE=https://api.openai.com/v1
```

支持 OpenAI 兼容 API（OpenAI、Azure、SiliconFlow、SiliconFlow 等）。

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/intelligence/stats` | 获取仪表盘统计 |
| GET | `/api/intelligence` | 获取情报列表 |
| GET | `/api/intelligence/{id}` | 获取情报详情 |
| POST | `/api/intelligence/ingest` | 摄入新情报 |
| DELETE | `/api/intelligence/{id}` | 删除情报 |
| POST | `/api/analysis/{id}` | 分析单条情报 |
| POST | `/api/analysis/batch` | 批量分析 |
| GET | `/api/analysis/{id}` | 获取分析报告 |

## 数据库

### 数据表

- `intelligence_items`: 情报条目主表
- `entities`: 提取的实体表
- `analysis_reports`: 分析报告表

### 切换数据库

```bash
# MySQL
export DATABASE_URL=mysql+aiomysql://user:pass@host:3306/blackagent

# PostgreSQL
export DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/blackagent
```

## 项目结构

```
blackagent/
├── backend/
│   ├── app/
│   │   ├── config.py       # 配置管理
│   │   ├── database.py    # 数据库配置
│   │   ├── models/        # ORM 模型
│   │   ├── routers/       # API 路由
│   │   ├── services/      # 业务服务
│   │   └── mock_data/     # 模拟数据生成
│   ├── main.py            # 应用入口
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/           # API 调用
│   │   ├── components/    # React 组件
│   │   ├── pages/         # 页面组件
│   │   └── types/         # TypeScript 类型
│   └── package.json
└── README.md
```

## 注意事项

⚠️ **免责声明**: 本项目仅供安全研究和教育目的使用。请勿将本工具用于任何非法活动。所有模拟数据均为虚构生成。

## License

MIT
