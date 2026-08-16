# 面向计算机类职业学习者的目标能力诊断与个性化学习资源生成系统

> 竞赛项目 · 开发中

## 项目简介

用户输入个人技能、项目经验、学习背景等自由文本，系统通过 AI 多智能体协同诊断其能力水平，识别知识薄弱点，并自动生成个性化的学习路径和学习资源。

## 技术栈

| 部分 | 选型 |
|------|------|
| 后端 | Python 3.10+（FastAPI） |
| 数据库 | SQLite |
| 向量库 | Qdrant（本地文件模式）+ BGE-M3 嵌入模型 |
| AI 推理 | DeepSeek API（含真实结果校准的串行 Agent，无 API 时自动降级为规则引擎） |
| 防幻觉 | DeepSeek API（复用 LLM 配置，比对知识库原文，无需额外部署） |
| 前端 | Vue 3 + Element Plus |

## 环境准备

### 1. Python 环境

需要 Python 3.10 或以上版本。

```bash
cd backend
pip install -r requirements.txt
```

> 依赖里 `FlagEmbedding` 会连带安装 PyTorch（体积较大）。国内直连慢，建议加镜像源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

### 2. LLM 配置（重要）

编辑 `backend/llm_config.json`，在 `api_key` 字段填入你的 API Key：

```json
{
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-flash",
  "api_key": "sk-你的key",
  "temperature": 0.7
}
```

> **获取 DeepSeek API Key：** 访问 [platform.deepseek.com](https://platform.deepseek.com) 注册并充值（最低充值 ¥1），在 API Keys 页面创建 Key。
>
> **不填 Key 也能用：** 系统会自动降级为规则引擎模式，输出模板化内容。接上 LLM 后内容质量会大幅提升。

支持任意 OpenAI 兼容的 API（OpenAI、阿里百炼、本地 vLLM 等），只需改这三个字段即可切换。

> 同一个 Key 同时用于主推理与防幻觉校验（见第 4 节），无需额外配置。

### 3. 向量库与嵌入模型

- **qdrant_storage 向量库**（2,269 条岗位知识片段）：本次交接包已附带与 `knowledge/active` 四个切片匹配的 `storage.sqlite`；如果只从 GitHub clone，需要从交接包补回该文件，或按知识库文档重新向量化。
- **BGE-M3 嵌入模型**（约 2.2GB）：**需自行下载**（体积过大，未随仓库分发）。从 HuggingFace 下载 `BAAI/bge-m3`，把整个模型目录放到 `backend/bge-m3/`。国内可设镜像 `HF_ENDPOINT=https://hf-mirror.com` 加速。

> 缺少模型时后端不会崩溃，但向量检索会返回空、资源生成退化为模板内容；补全后即恢复完整效果。BGE-M3 首次加载约 20~40 秒，加载后常驻内存。

### 4. 防幻觉校验（无需单独部署）

防幻觉校验复用 `backend/llm_config.json` 里的 DeepSeek API（与主推理同一个 Key），比对生成内容与知识库原文、判断是否编造。第 2 步配置好 LLM 后即自动可用，无需安装本地模型。

### 5. Node.js 环境

需要 Node.js 18 或以上版本。

```bash
cd frontend
npm install
```

## 快速启动

### 后端

```bash
cd backend
python main.py
```

启动后访问 `http://localhost:8000/docs` 查看 API 文档。

### 前端

```bash
cd frontend
npm run dev
```

启动后访问 `http://localhost:5173`，登录后即可使用。

> 默认注册的第一个账号即为可用账号，直接用任一用户名+密码注册即可。

## 项目结构

```
├── backend/
│   ├── main.py                 # FastAPI 入口
│   ├── config.py               # 配置
│   ├── database.py             # 数据库连接
│   ├── dimensions.py           # 能力维度定义
│   ├── requirements.txt        # Python 依赖
│   ├── llm_config.json         # ★ LLM 配置（API Key、模型地址）
│   ├── capability_diagnosis.db # SQLite 数据库
│   ├── bge-m3/                 # ★ BGE-M3 嵌入模型（需自行下载，不随仓库分发）
│   ├── qdrant_storage/         # Qdrant 向量知识库（2,269 条，已随仓库分发）
│   ├── models/                 # ORM 模型
│   ├── routers/                # API 路由
│   ├── adapters/               # 适配层
│   │   ├── agent_adapter.py    # Agent 对外接口
│   │   ├── agent_runtime.py    # Agent 运行时（串行 Agent 与真实结果校准）
│   │   ├── llm_client.py       # LLM 客户端（OpenAI 兼容）
│   │   ├── vector_adapter.py   # 向量检索适配（Qdrant + BGE-M3）
│   │   └── guardrail.py        # 防幻觉校验（比对知识库原文）
│   └── tests/                  # 测试脚本
│
├── frontend/
│   └── src/
│       ├── api/                # 后端接口封装
│       ├── components/         # 公共组件
│       ├── router/             # 路由配置
│       ├── stores/             # Pinia 状态管理
│       ├── styles/             # 主题样式
│       └── views/              # 页面组件
│
└── README.md                   # 本文件
```

## AI Agent 流水线

```
用户自由文本
  → 资料审查（AI 判断描述是否充分，不足则提示补充）
  → 自由文本学情解析 Agent（LLM 语义理解 / 关键词匹配降级）
  → 岗位知识库检索 Agent（Qdrant + BGE-M3 向量检索）
  → 岗位能力诊断 Agent（生成 16 维能力向量 + 知识缺口）
  → 诊断结果校正 Agent（校验字段、数值范围、文本充分度）
  → 真实结果校准 Agent（对照客观题/实操/专家标注计算准确率，可选纠正）
  → 防幻觉校验（DeepSeek 比对知识库原文）
  → 个性化资源生成 Agent（基于检索片段生成讲义/练习/案例）
  → 层2 资源校验（比对原文，标记 passed / partial / blocked）
  → 个性化学习路径 Agent（按能力缺口规划 8 步学习路径）
```

多个 Agent 串行执行，每个 Agent 有独立身份（system prompt），LLM 不可用时自动降级为确定性规则引擎。真实结果校准 Agent 不使用模型置信度代替准确率：没有真实标注时状态为 `unvalidated`，只有接入可信的客观题、实操结果或专家标注后才计算准确率。

准确率相关接口和数据格式详见 [`GROUND_TRUTH_CALIBRATION.md`](GROUND_TRUTH_CALIBRATION.md)。

## 四个岗位能力模型

| 岗位 | 技能数 | 核心维度 | 知识库片段 |
|------|--------|---------|-----------|
| 前端开发工程师 | 16 项 | 前端技术、编程基础 | 518 |
| 后端开发工程师 | 16 项 | 编程基础、数据结构与算法、后端技术、数据库、系统设计 | 1,149 |
| 运维工程师 | 16 项 | 计算机网络、操作系统、运维部署、安全规范 | 588 |
| 产品经理 | 16 项 | 产品分析、项目管理、沟通表达、逻辑思维 | 14 |

## 常见问题

### 首次诊断等待很久

首次提交诊断时 BGE-M3 模型（2.2GB）需要加载到内存，约 20~40 秒。加载后常驻内存，后续请求恢复正常速度。

### "个性化学习"内容重复/模板化

说明 LLM 未接入。检查 `backend/llm_config.json` 中的 `api_key` 是否已填写正确。

### 端口被占用

```bash
# Windows 查看 8000 端口占用
netstat -ano | findstr :8000
# 记下 PID，然后杀掉
taskkill -F -PID <PID>
```

### 后端启动报错 ModuleNotFoundError

依赖未安装或版本过旧：

```bash
cd backend
pip install -r requirements.txt
```

### 向量检索返回空

`backend/bge-m3/` 目录缺失（需自行下载，见第 3 节）；`backend/qdrant_storage/` 缺失或损坏则从队友处获取最新知识库文件。
