# 职学导航：目标能力诊断与个性化培训资源生成系统

面向计算机类职业学习者的多 Agent 能力诊断、资料审查与个性化培训资源生成平台。

系统服务于已经明确目标岗位、但需要判断自身能力是否达标的学习者。用户提交学习描述、简历、项目材料和课程记录后，系统提取能力证据，对照岗位能力模型识别差距，再基于领域知识库生成学习路径与培训资源，并对生成内容进行来源校验。

## 核心闭环

```text
选择目标岗位
  -> 提交自由文本或学习材料
  -> 资料充分性审查
  -> 多 Agent 能力诊断
  -> 真实结果校准
  -> 生成学习路径与培训资源
  -> 知识库来源校验与审核纠偏
  -> 学习、收藏、完成记录与复测
```

当前内置四个数字技术岗位方向：

- 前端开发工程师
- 后端开发工程师
- 运维工程师
- 产品经理

## 已实现功能

### 用户与资料

- 用户注册、登录、JWT 身份认证和密码修改
- PDF、Word、文本、代码和常见图片资料上传
- 用户资料解析、列表、下载和删除
- 自由文本学习经历补充

### 诊断与 Agent

- 输入充分性审查，不足时返回针对性补充建议
- 资料解析、能力诊断、路径规划、资源生成、审核纠偏串行协作
- 16 维能力向量、能力矩阵、知识缺口和岗位匹配结果
- 基于客观题、实操结果或专家标注的真实结果校准
- 当前 Agent、阶段说明、百分比和最近事件实时展示
- Agent 执行轨迹与知识库检索来源查询

### 知识库与资源

- Qdrant 本地向量库与 BGE-M3 语义检索
- 讲义、练习、实操任务等个性化资源生成
- `source_chunk_id`、`source_text` 与生成资源绑定
- 生成内容与知识库原文比对，输出 `passed`、`partial` 或 `blocked`
- 资源搜索、筛选、详情、收藏与取消收藏
- 开始学习、完成学习和真实学习进度记录

## 系统架构

| 层级 | 技术与职责 |
|---|---|
| 前端 | Vue 3、TypeScript、Vite、Pinia、Element Plus、ECharts |
| API | FastAPI 提供认证、资料、诊断、Agent、资源与学习记录接口 |
| 业务数据 | SQLAlchemy + SQLite；部署时可迁移至 PostgreSQL/MySQL |
| 向量检索 | Qdrant 本地存储岗位知识片段 |
| Embedding | BGE-M3 将查询与知识片段编码为向量 |
| Agent 编排 | Python 串行运行时、独立 Prompt、结构化 JSON 输出 |
| 大模型 | DeepSeek 或任意 OpenAI 兼容 API |
| 防幻觉 | 检索原文绑定、规则拦截和外部大模型二次校验 |

## Agent 工作流

```text
资料解析 Agent
  -> 能力诊断 Agent
  -> 真实结果校准 Agent
  -> 路径规划 Agent
  -> 资源生成 Agent
  -> 审核纠偏 Agent
```

每个阶段使用独立 Prompt 和结构化输出约束。LLM 不可用时，诊断模块会降级到确定性规则逻辑；知识库没有可靠来源时，资源不得以正式可信资源状态写入。

置信度与准确率是两个不同指标：

- 置信度描述系统对单次诊断依据充分程度的估计。
- 准确率必须使用客观题、实操结果或专家标注作为真实值计算。
- 没有真实标注时，校准状态为 `unvalidated`，不会用置信度代替准确率。

详细规则参见 [GROUND_TRUTH_CALIBRATION.md](GROUND_TRUTH_CALIBRATION.md)。

## 实时 Agent 进度

诊断执行期间，后端维护有界进度事件序列，前端约每 0.9 秒读取一次：

```http
GET /api/assessment/{assessment_id}/progress
```

响应示例：

```json
{
  "stage": "resource",
  "agent": "资源生成 Agent",
  "label": "正在生成学习资源 (3/8)",
  "percent": 68,
  "status": "running",
  "updated_at": "2026-08-17T05:00:00Z",
  "events": []
}
```

阶段包括 `material`、`diagnosis`、`path`、`resource`、`review` 和 `complete`。失败时进度不会被清空，而是返回 `failed`，便于前端终止动画并提示重试。

> 当前进度事件保存在后端进程内，适用于本地演示和单 Worker 部署。采用多 Worker 或多服务器部署时，应将进度状态迁移到 Redis，并按 `assessment_id` 设置过期时间，避免负载均衡后读取到不同进程的数据。

## 登录与权限

- 后端业务接口通过 Bearer Token 校验当前用户。
- 用户只能读取和修改自己的评估、资料、资源收藏及学习记录。
- 首页与登录页允许公开访问。
- 资料审查、能力诊断、资料库、资源详情和个人中心默认需要登录。
- `VITE_PUBLIC_PREVIEW=true` 只用于本地视觉验收，仅跳过前端路由守卫，不会绕过后端接口认证。
- 正式运行和生产构建不得启用公开预览。

生产环境必须设置新的 JWT 密钥：

```env
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_EXPIRE_MINUTES=1440
```

## 环境要求

- Python 3.10+
- Node.js 18+
- 约 3 GB 可用磁盘空间用于依赖和 BGE-M3
- DeepSeek 或其他 OpenAI 兼容 API Key（可选，但建议配置）

## 安装

### 后端

```bash
cd backend
python -m venv .venv
```

Windows：

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux/macOS：

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

`FlagEmbedding` 会安装 PyTorch，下载时间和体积较大。网络受限时可使用可信镜像源。

### 前端

```bash
cd frontend
npm install
```

## LLM 配置

编辑 `backend/llm_config.json`：

```json
{
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-v4-flash",
  "api_key": "sk-your-api-key",
  "temperature": 0.7,
  "trust_env": false
}
```

该客户端兼容 OpenAI API 协议。切换模型服务时，需要同步验证模型名称、JSON 输出稳定性、上下文长度和计费策略。

不要把真实 API Key 提交到 Git。部署时建议通过密钥管理服务或环境挂载配置文件。

## 知识库准备

完整检索需要以下两部分：

1. `backend/qdrant_storage/`：Qdrant 本地集合，保存岗位知识向量与原始片段元数据。
2. `backend/bge-m3/`：BGE-M3 模型目录，约 2.2 GB，不随 Git 仓库分发。

从 Hugging Face 下载模型：

```bash
huggingface-cli download BAAI/bge-m3 --local-dir backend/bge-m3
```

国内网络可临时设置：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

缺少模型时后端仍可启动，但向量检索和资源来源质量会下降。不得把“接口可运行”当作“知识库已完整接入”。

## 启动

### 1. 启动后端

```bash
cd backend
python main.py
```

- API 地址：`http://localhost:8000`
- Swagger：`http://localhost:8000/docs`

### 2. 启动前端

```bash
cd frontend
npm run dev
```

- 页面地址：`http://localhost:5173`
- Vite 默认将 `/api` 代理到 `http://localhost:8000`
- 可用 `VITE_API_PROXY_TARGET` 指定其他后端地址

访问受保护页面前，需要先完成注册或登录。

## 主要 API

| 模块 | 接口 | 说明 |
|---|---|---|
| 认证 | `POST /api/auth/register` | 注册 |
| 认证 | `POST /api/auth/login` | 登录并获取 Token |
| 认证 | `GET /api/auth/me` | 当前用户 |
| 岗位 | `GET /api/jobs/list` | 岗位能力模型列表 |
| 资料 | `POST /api/material/upload` | 上传并解析资料 |
| 资料 | `POST /api/material/text` | 保存文本证据 |
| 评估 | `POST /api/assessment/create` | 创建评估 |
| 评估 | `POST /api/assessment/review-input` | 审查输入充分性 |
| 评估 | `POST /api/assessment/{id}/submit` | 执行诊断与资源生成 |
| 评估 | `GET /api/assessment/{id}/progress` | 实时进度事件 |
| 评估 | `GET /api/assessment/{id}/agents` | Agent 轨迹与检索来源 |
| 校准 | `POST /api/assessment/{id}/calibrate` | 提交真实标注并校准 |
| 资源 | `GET /api/resource/list` | 用户资源列表 |
| 资源 | `GET /api/resource/search` | 搜索资源 |
| 收藏 | `POST /api/resource/{id}/bookmark` | 收藏资源 |
| 收藏 | `DELETE /api/resource/{id}/bookmark` | 取消收藏 |
| 学习 | `POST /api/record/resource/{id}/start` | 开始或继续学习 |
| 学习 | `PUT /api/record/{id}/complete` | 完成学习 |

## 数据与证据链

核心业务模型包括：

- `User`
- `Job`
- `UserMaterial`
- `Assessment`
- `CalibrationRecord`
- `LearningPath`
- `Resource`
- `ResourceBookmark`
- `LearningRecord`
- `Session`（学习会话）

资源通过评估、能力缺口与知识库来源形成追溯关系：

```text
assessment_id
  -> requirement_id / gap_id
  -> source_chunk_id + source_text
  -> generated resource
  -> review_status + review_reason
```

## 项目结构

```text
PK-MACDM/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── llm_config.json
│   ├── adapters/
│   │   ├── agent_adapter.py
│   │   ├── agent_runtime.py
│   │   ├── calibration.py
│   │   ├── guardrail.py
│   │   ├── llm_client.py
│   │   └── vector_adapter.py
│   ├── models/
│   ├── prompts/
│   ├── routers/
│   ├── tests/
│   ├── qdrant_storage/
│   └── bge-m3/
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── router/
│   │   ├── stores/
│   │   └── views/
│   └── vite.config.ts
├── GROUND_TRUTH_CALIBRATION.md
└── README.md
```

## 测试

后端：

```bash
cd backend
python -m pytest tests -q
```

前端：

```bash
cd frontend
npm run build
```

当前自动化测试覆盖校准数据持久化、资源收藏、学习进度、评估删除清理和 Agent 进度事件。比赛指标仍需使用独立测试集、人工标注和真实学习者样本计算，不能只引用单元测试通过率。

## 安全说明

- 不要提交真实 API Key、生产数据库、用户上传资料或 JWT 密钥。
- 防幻觉校验不能替代人工专家审核，尤其是代码安全、运维安全和职业评价结论。
- “准确率达到 90%”必须由有真实标签的独立测试集验证，不能由模型自报置信度得出。
- 对外部署前应增加 HTTPS、限流、日志脱敏、备份、上传文件校验和 Redis 共享任务状态。
