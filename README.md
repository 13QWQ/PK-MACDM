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
| AI 推理 | Qwen2.5 + 多 Agent 协同 |
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
│   │   ├── agent_adapter.py     # AI 诊断接口适配
│   │   ├── graph_adapter.py     # 知识图谱接口适配
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
| AI 诊断 | 🚧 Mock 数据，待队友 Agent 接口 |
| AI 资源生成 | 🚧 Mock 数据，待队友 Agent 接口 |
| AI 路径规划 | 🚧 Mock 数据，待队友 Agent 接口 |
| 防幻觉层 | ⬜ 未开始 |

> AI 诊断、资源生成、路径规划当前均使用 Mock 数据返回，数据结构与真实接口一致。队友 Agent 接口就绪后，只需修改 `adapters/agent_adapter.py` 中的 3 处 TODO 即可切换。

## 队友接口说明

队友需提供的接口（详细定义见 `开发计划.md` 第四部分）：

| 优先级 | 接口 | 功能 | 状态 |
|--------|------|------|------|
| Demo 必需 | 向量检索 | ChromaDB + Ollama 文档检索 | ✅ 已接入 |
| 核心 | 能力诊断 | 分析用户能力，输出知识薄弱点 | 🚧 Mock |
| 核心 | 学习资源生成 | 根据知识点生成学习内容 | 🚧 Mock |
| 核心 | 学习路径规划 | 生成个性化学习路径 | 🚧 Mock |
| 重要 | 相似案例检索 | 检索相似用户案例 | ⬜ 未开始 |

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

### AI Agent 接口（待队友提供）

队友 Agent 接口就绪后，只需修改 `adapters/agent_adapter.py` 中 3 个函数的 TODO 部分即可接入真实 AI，适配层会自动将队友的接口格式转换为业务代码的统一格式。
