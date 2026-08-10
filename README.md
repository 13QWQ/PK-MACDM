# 面向计算机类职业学习者的目标能力诊断与个性化学习资源生成系统

> 竞赛项目 · 开发中

## 项目简介

用户输入个人技能、项目经验、学习背景等自由文本，系统通过 AI 多智能体协同诊断其能力水平，识别知识薄弱点，并自动生成个性化的学习路径和学习资源。

## 技术栈

| 部分 | 选型 |
|------|------|
| 后端 | Python（FastAPI） |
| 数据库 | SQLite（开发）/ MySQL（生产） |
| 向量库 | ChromaDB + Ollama（nomic-embed-text） |
| AI 推理 | 多 Agent 协同（纯 Python 确定性逻辑，6 个串行 Agent） |
| 前端 | Vue 3 + Element Plus |

## 快速启动

### 后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

后端启动后访问 `http://localhost:8000/docs` 查看 API 文档。

> **注意：** 向量检索功能需要本地运行 Ollama 服务并拉取 `nomic-embed-text` 模型，否则搜索接口返回空结果。其余接口不受影响。

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端启动后访问 `http://localhost:5173`。

## 项目结构

```
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置
│   ├── database.py          # 数据库连接
│   ├── dimensions.py        # 能力维度定义
│   ├── requirements.txt     # Python 依赖
│   ├── capability_diagnosis.db  # SQLite 数据库
│   ├── models/              # ORM 模型
│   ├── routers/             # API 路由
│   ├── adapters/            # 适配层（隔离队友接口变动）
│   │   ├── agent_adapter.py     # Agent 对外接口（3 个核心函数）
│   │   ├── agent_runtime.py     # Agent 运行时（6 个串行 Agent）
│   │   ├── graph_adapter.py     # 知识图谱接口适配（已弃用）
│   │   ├── vector_adapter.py    # 向量检索接口适配
│   │   └── mock_data.py         # Mock 数据
│   ├── my_vector_db/        # 向量库 - 产品经理
│   ├── db_frontend/         # 向量库 - 前端开发
│   ├── db_backend/          # 向量库 - 后端开发
│   └── db_ops/              # 向量库 - 运维
│
├── frontend/
│   └── src/
│       ├── api/              # 后端接口封装
│       ├── components/       # 公共组件
│       ├── router/           # 路由配置
│       ├── stores/           # Pinia 状态管理
│       ├── styles/           # 主题样式
│       └── views/            # 页面组件
│
└── README.md                # 本文件
```

## 当前进度

| 模块 | 状态 |
|------|------|
| 后端（FastAPI） | ✅ 已完成 |
| 前端（Vue 3） | ✅ 已完成 |
| 前后端联调 | ✅ 已完成 |
| RAG 检索 | ✅ 已接入（4 岗位向量库） |
| AI Agent（6 个串行） | ✅ 已接入（纯 Python，不依赖外部模型 API） |
| 防幻觉层 | 🚧 Mock（审核纠偏函数预留，待 source_chunk_id 字段补齐后接入） |

> Agent 无需外部模型 API 即可运行。关闭 Ollama 时，诊断仍正常输出，资源生成会提示无知识库来源而非伪造内容。

## 队友接口说明

队友提供的接口：

| 接口 | 功能 | 状态 |
|------|------|------|
| 向量检索 | ChromaDB + Ollama 文档检索 | ✅ 已接入 |
| 能力诊断 | 多 Agent 分析，输出能力向量 + 知识缺口 | ✅ 已接入 |
| 学习资源生成 | 基于知识库片段组装资源内容 | ✅ 已接入 |
| 学习路径规划 | 按能力排序生成学习步骤 | ✅ 已接入 |
| 内容审核纠偏 | 校验资源来源，无来源则阻断 | 🚧 Mock（待字段补齐） |

### RAG 向量检索（已接入）

队友通过 ChromaDB + Ollama（`nomic-embed-text`）提供了 4 个岗位的知识库向量数据，已通过适配层接入后端：

**4 个向量集合：**

| 岗位 | ChromaDB 目录 | 集合名 |
|------|-------------|--------|
| 产品经理 | `my_vector_db/` | `product_kb` |
| 前端开发工程师 | `db_frontend/` | `frontend_kb` |
| 后端开发工程师 | `db_backend/` | `backend_kb` |
| 运维工程师 | `db_ops/` | `ops_kb` |

**API 端点：**

```
GET /api/resource/search?q=需求分析&job=产品经理&top_k=5
```

后端 `adapters/vector_adapter.py` 中的 `JOB_COLLECTION_MAP` 负责岗位名 → 目录/集合的路由。加新岗位只需在映射表加一行。

### AI Agent（已接入）

`agent_runtime.py` 包含 6 个串行 Agent，覆盖四个岗位（前端、后端、运维、产品经理），不依赖外部模型 API：

```
用户自由文本
  → 自由文本学情解析 Agent（关键词匹配 + 否定表述识别）
  → 岗位知识库检索 Agent（调 ChromaDB 检索相关片段）
  → 岗位能力诊断 Agent（生成 16 维能力向量 + 知识缺口）
  → 诊断结果校正 Agent（校验字段、数值范围、文本充分度）
  → 个性化资源生成 Agent（基于检索片段组装内容，无来源则阻断）
  → 个性化学习路径 Agent（按能力排序生成学习步骤）
```

所有 Agent 输出通过 `agent_adapter.py` 的三个函数（`diagnose` / `generate_resource` / `plan_learning_path`）暴露，前端接口无变化。
