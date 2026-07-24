# 面向计算机类职业学习者的目标能力诊断与个性化学习资源生成系统

> 竞赛项目 · 开发中

## 项目简介

用户输入个人技能、项目经验、学习背景等自由文本，系统通过 AI 多智能体协同诊断其能力水平，识别知识薄弱点，并自动生成个性化的学习路径和学习资源。

## 技术栈

| 部分 | 选型 |
|------|------|
| 后端 | Python（FastAPI） |
| 数据库 | SQLite（开发）/ MySQL（生产） |
| 向量库 | Milvus / FAISS |
| AI 推理 | Qwen2.5 + 多 Agent 协同 |
| 前端 | Vue 3 + Element Plus |

## 快速启动

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

后端启动后访问 `http://localhost:8000/docs` 查看 API 文档。

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
│   ├── models/               # ORM 模型
│   ├── routers/              # API 路由
│   └── adapters/             # 适配层（隔离队友接口变动）
│       ├── agent_adapter.py  # AI 诊断接口适配
│       ├── graph_adapter.py  # 知识图谱接口适配
│       └── vector_adapter.py # 向量库接口适配
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
| RAG 检索 | 🚧 队友开发中 |
| AI API 对接 | ⬜ 未开始 |
| 防幻觉层 | ⬜ 未开始 |
| 知识图谱 | ❌ 已砍掉 |

> 当前所有 AI 功能均使用 Mock 数据，队友接口就绪后通过适配层接入。

## 队友接口说明

队友需提供的接口（详细定义见 `开发计划.md` 第四部分）：

| 优先级 | 接口 | 功能 |
|--------|------|------|
| Demo 必需 | `search_resources(query, top_k)` | RAG 文档检索 |
| 核心 | 能力诊断 | 分析用户能力，输出知识薄弱点 |
| 核心 | 学习资源生成 | 根据知识点生成学习内容 |
| 核心 | 学习路径规划 | 生成个性化学习路径 |
| ❌ | ~~查询知识点关系~~ | 已砍掉 |
| ❌ | ~~查询职业能力图谱~~ | 已砍掉 |
| 重要 | 相似案例检索 | 检索相似用户案例 |

Demo 阶段队友只需要做一个接口：

```python
def search_resources(query, top_k=5):
    """RAG 文档检索"""
    return [
        {
            "title": "文档名",
            "content": "搜到的内容片段",
            "score": 0.95         # 匹配度 0~1
        }
    ]
```
