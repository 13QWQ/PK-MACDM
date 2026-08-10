"""Role-aware, deterministic multi-Agent runtime for the reference backend.

This module has no dependency on a model vendor.  It uses the existing
``adapters.vector_adapter.search_similar_resources`` function as its RAG
boundary and can therefore run before a real DeepSeek/Qwen API is connected.

The runtime is deliberately shaped around the backend repository's public
contracts:

* diagnose(user_id, target_job, user_input)
* generate_resource(knowledge_point, user_level, resource_type)
* plan_learning_path(user_id, target_job, current_ability)

The user supplies one free-text description.  Scores and weekly study hours
are not additional inputs to this layer.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
import re
from typing import Any, Callable, Protocol
from uuid import uuid4


DIMENSIONS = [
    (1, "编程基础", "通用基础"),
    (2, "数据结构与算法", "通用基础"),
    (3, "计算机网络", "通用基础"),
    (4, "操作系统", "通用基础"),
    (5, "前端技术", "专业方向"),
    (6, "后端技术", "专业方向"),
    (7, "数据库", "专业方向"),
    (8, "系统设计", "专业方向"),
    (9, "运维部署", "专业方向"),
    (10, "测试与质量", "专业方向"),
    (11, "产品分析", "专业方向"),
    (12, "项目管理", "专业方向"),
    (13, "沟通表达", "综合素质"),
    (14, "逻辑思维", "综合素质"),
    (15, "学习能力", "综合素质"),
    (16, "安全规范", "综合素质"),
]


JOB_ALIASES = {
    "前端工程师": "前端开发工程师",
    "前端开发": "前端开发工程师",
    "后端工程师": "后端开发工程师",
    "后端开发": "后端开发工程师",
    "Java后端工程师": "后端开发工程师",
    "java后端工程师": "后端开发工程师",
    "运维": "运维工程师",
    "DevOps工程师": "运维工程师",
    "产品": "产品经理",
}


def normalize_job(job: str) -> str:
    name = str(job or "").strip()
    return JOB_ALIASES.get(name, name)


# The profile is intentionally kept in the Agent package so all four roles
# follow the same workflow.  The repository's job seed data remains the UI
# source of truth; these lists are the Agent's scoring and retrieval keywords.
ROLE_PROFILES: dict[str, dict[str, Any]] = {
    "前端开发工程师": {
        "skills": [
            ("HTML", "前端技术"), ("CSS", "前端技术"),
            ("JavaScript", "前端技术"), ("Vue", "前端技术"),
            ("React", "前端技术"), ("TypeScript", "前端技术"),
            ("浏览器原理", "前端技术"), ("响应式设计", "前端技术"),
            ("Webpack/Vite", "前端技术"), ("前端性能优化", "前端技术"),
            ("API设计", "后端技术"), ("接口联调", "后端技术"),
            ("Git", "项目管理"), ("单元测试", "测试与质量"),
            ("网络协议", "计算机网络"), ("安全编码", "安全规范"),
        ],
        "weights": {"前端技术": "high", "编程基础": "high", "后端技术": "mid", "数据库": "mid", "测试与质量": "mid", "沟通表达": "mid"},
    },
    "后端开发工程师": {
        "skills": [
            ("Python", "编程基础"), ("Java", "编程基础"),
            ("数据结构与算法", "数据结构与算法"), ("Spring Boot", "后端技术"),
            ("FastAPI", "后端技术"), ("API设计", "后端技术"),
            ("并发编程", "后端技术"), ("MySQL", "数据库"),
            ("Redis", "数据库"), ("系统设计", "系统设计"),
            ("Linux", "操作系统"), ("Docker", "运维部署"),
            ("Git", "项目管理"), ("单元测试", "测试与质量"),
            ("认证与授权", "安全规范"), ("网络协议", "计算机网络"),
        ],
        "weights": {"编程基础": "high", "数据结构与算法": "high", "后端技术": "high", "数据库": "high", "系统设计": "high", "计算机网络": "mid", "操作系统": "mid", "运维部署": "mid", "测试与质量": "mid", "安全规范": "mid", "学习能力": "mid"},
    },
    "运维工程师": {
        "skills": [
            ("Linux", "操作系统"), ("网络协议", "计算机网络"),
            ("Docker", "运维部署"), ("Kubernetes", "运维部署"),
            ("Nginx", "运维部署"), ("Shell脚本", "编程基础"),
            ("监控告警", "运维部署"), ("CI/CD", "运维部署"),
            ("日志管理", "运维部署"), ("故障排查", "运维部署"),
            ("数据库", "数据库"), ("安全规范", "安全规范"),
            ("云服务", "运维部署"), ("Git", "项目管理"),
            ("自动化测试", "测试与质量"), ("系统设计", "系统设计"),
        ],
        "weights": {"计算机网络": "high", "操作系统": "high", "运维部署": "high", "安全规范": "high", "后端技术": "mid", "数据库": "mid", "测试与质量": "mid", "编程基础": "mid", "系统设计": "mid"},
    },
    "产品经理": {
        "skills": [
            ("需求分析", "产品分析"), ("用户研究", "产品分析"),
            ("产品设计", "产品分析"), ("数据分析", "产品分析"),
            ("竞品分析", "产品分析"), ("业务理解", "产品分析"),
            ("原型设计", "产品分析"), ("文档撰写", "沟通表达"),
            ("沟通协调", "沟通表达"), ("项目推进", "项目管理"),
            ("项目管理", "项目管理"), ("逻辑思维", "逻辑思维"),
            ("技术理解", "编程基础"), ("接口基础", "后端技术"),
            ("数据安全", "安全规范"), ("用户体验", "产品分析"),
        ],
        "weights": {"产品分析": "high", "项目管理": "high", "沟通表达": "high", "逻辑思维": "high", "学习能力": "mid", "前端技术": "mid", "后端技术": "low", "数据分析": "high"},
    },
}


class Retriever(Protocol):
    def search(self, query: str, job: str, top_k: int = 5) -> list[dict[str, Any]]:
        ...


class BackendVectorRetriever:
    """Lazy bridge to the reference backend's existing Chroma adapter."""

    def search(self, query: str, job: str, top_k: int = 5) -> list[dict[str, Any]]:
        try:
            from adapters.vector_adapter import search_similar_resources

            return search_similar_resources(query=query, job=job, top_k=top_k)
        except Exception:
            # The backend already defines empty-result degradation when Ollama
            # is unavailable.  Keep this layer equally non-fatal.
            return []


@dataclass
class AgentEvent:
    name: str
    status: str
    input_summary: str
    output_summary: str
    confidence: float
    review_result: str | None = None


@dataclass
class ParsedProfile:
    text: str
    matched_skills: dict[str, float] = field(default_factory=dict)
    negative_skills: set[str] = field(default_factory=set)
    action_evidence_count: int = 0
    retrieval_hits: list[dict[str, Any]] = field(default_factory=list)


class InputParsingAgent:
    name = "自由文本学情解析 Agent"

    def run(self, target_job: str, user_input: str) -> ParsedProfile:
        text = re.sub(r"\s+", " ", str(user_input or "")).strip()
        profile = ParsedProfile(text=text)
        role = ROLE_PROFILES.get(target_job, ROLE_PROFILES["后端开发工程师"])
        action_terms = "掌握|熟悉|使用|实现|开发|负责|搭建|设计|部署|维护|优化|排查|完成|参与|实习|工作|项目"
        profile.action_evidence_count = len(re.findall(action_terms, text, flags=re.IGNORECASE))

        for skill, _dimension in role["skills"]:
            if not _contains_skill(text, skill):
                continue
            if _is_negative_claim(text, skill):
                profile.negative_skills.add(skill)
                profile.matched_skills[skill] = 0.2
                continue
            context = _skill_context(text, skill)
            has_action = bool(re.search(action_terms, context, flags=re.IGNORECASE))
            profile.matched_skills[skill] = 0.72 if has_action else 0.52
        return profile


class RAGEvidenceAgent:
    name = "岗位知识库检索 Agent"

    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    def run(self, target_job: str, profile: ParsedProfile, events: list[AgentEvent]) -> None:
        role = ROLE_PROFILES[target_job]
        queries = list(profile.matched_skills) or [skill for skill, _ in role["skills"][:5]]
        for skill in queries[:8]:
            hits = self.retriever.search(f"{target_job} {skill}", target_job, top_k=2)
            profile.retrieval_hits.extend(
                [{"query": skill, "job": target_job, **hit} for hit in hits]
            )
        events.append(AgentEvent(
            name=self.name,
            status="completed",
            input_summary=f"按 {target_job} 知识库检索 {min(len(queries), 8)} 个能力关键词。",
            output_summary=f"返回 {len(profile.retrieval_hits)} 条 RAG 片段。",
            confidence=0.88 if profile.retrieval_hits else 0.55,
        ))


class CapabilityScoringAgent:
    name = "岗位能力诊断 Agent"

    def run(self, target_job: str, profile: ParsedProfile, events: list[AgentEvent]) -> dict[str, Any]:
        role = ROLE_PROFILES[target_job]
        skill_by_dimension: dict[str, list[float]] = {name: [] for _, name, _ in DIMENSIONS}
        gaps: list[tuple[str, float]] = []
        for skill, dimension in role["skills"]:
            value = profile.matched_skills.get(skill, 0.18)
            if skill in profile.negative_skills:
                value = 0.2
            skill_by_dimension.setdefault(dimension, []).append(value)
            if value < 0.60:
                gaps.append((skill, value))

        vector: list[dict[str, Any]] = []
        for index, name, category in DIMENSIONS:
            values = skill_by_dimension.get(name) or [0.18]
            value = min(0.92, max(0.12, sum(values) / len(values)))
            weight = role["weights"].get(name, "low")
            vector.append({
                "index": index,
                "name": name,
                "value": round(value, 4),
                "weight": weight,
                "category": category,
            })

        gap_names = [skill for skill, _value in sorted(gaps, key=lambda item: item[1])[:5]]
        if not gap_names:
            gap_names = [skill for skill, _ in role["skills"][:3]]

        weight_value = {"high": 1.6, "mid": 1.0, "low": 0.5}
        numerator = sum(item["value"] * weight_value[item["weight"]] for item in vector)
        denominator = sum(weight_value[item["weight"]] for item in vector)
        overall = round(numerator / denominator, 4)
        coverage = len(profile.matched_skills) / len(role["skills"])
        confidence = min(0.92, max(0.35, 0.48 + min(0.18, len(profile.text) / 600) + min(0.18, coverage * 0.45) + (0.08 if profile.action_evidence_count else 0)))

        events.append(AgentEvent(
            name=self.name,
            status="completed",
            input_summary=f"对照 {len(role['skills'])} 个岗位能力项，输入长度 {len(profile.text)} 字。",
            output_summary=f"生成 16 维能力向量，识别 {len(gap_names)} 个薄弱知识点。",
            confidence=round(confidence, 2),
        ))
        return {
            "overall_mastery": overall,
            "ability_vector": vector,
            "knowledge_gaps": gap_names,
            "confidence": round(confidence, 2),
        }


class CalibrationAgent:
    name = "诊断结果校正 Agent"

    def run(self, diagnosis: dict[str, Any], profile: ParsedProfile, events: list[AgentEvent]) -> dict[str, Any]:
        errors: list[str] = []
        vector = diagnosis.get("ability_vector")
        if not isinstance(vector, list) or len(vector) != 16:
            errors.append("ability_vector 必须包含 16 个维度")
        for item in vector or []:
            value = item.get("value")
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                errors.append(f"维度 {item.get('name')} 的 value 不在 0 到 1 范围内")
        if not isinstance(diagnosis.get("knowledge_gaps"), list):
            errors.append("knowledge_gaps 必须是字符串列表")
        if len(profile.text) < 10:
            diagnosis["confidence"] = min(float(diagnosis.get("confidence", 0.4)), 0.45)
        events.append(AgentEvent(
            name=self.name,
            status="completed" if not errors else "rejected",
            input_summary="校验诊断输出字段、向量长度、数值范围和自由文本证据充分度。",
            output_summary="诊断结果通过结构校验。" if not errors else "诊断结果需要退回修正。",
            confidence=1.0 if not errors else 0.2,
            review_result="approved" if not errors else "rejected",
        ))
        if errors:
            raise ValueError("；".join(errors))
        return diagnosis


class ResourceAgent:
    name = "个性化资源生成 Agent"

    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    def run(self, knowledge_point: str, user_level: float, resource_type: str, target_job: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        hits = self.retriever.search(f"{target_job} {knowledge_point}", target_job, top_k=3)
        title = f"{knowledge_point}{resource_type}"
        difficulty = min(5, max(1, int(round(float(user_level or 0.2) * 5)) + (1 if resource_type == "练习" else 0)))
        if not hits:
            body = "当前岗位知识库未返回可用来源，本次不生成正式学习内容，请先检查 RAG 服务或补充知识库。"
            return {
                "content_type": resource_type,
                "title": title,
                "body": body,
                "difficulty": difficulty,
            }, []

        source = hits[0]
        source_title = str(source.get("title") or source.get("filename") or "岗位知识库片段")
        source_content = str(source.get("content") or "").strip()
        source_content = source_content[:1600]
        if resource_type == "讲义":
            body = f"学习目标：理解并能解释“{knowledge_point}”。\n\n知识库依据：{source_title}\n\n核心内容：\n{source_content}\n\n自检要求：用自己的话说明关键概念，并写出一个与目标岗位相关的使用场景。"
        elif resource_type == "练习":
            body = f"练习主题：{knowledge_point}\n\n参考依据：{source_title}\n\n任务：\n1. 从知识库片段中提取一个可验证的技术目标。\n2. 完成一个最小可运行示例。\n3. 记录输入、输出、异常处理和复盘结论。\n\n参考内容：\n{source_content}"
        elif resource_type == "案例":
            body = f"案例任务：围绕“{knowledge_point}”完成一次岗位化问题拆解。\n\n知识库依据：{source_title}\n\n案例材料：\n{source_content}\n\n交付物：方案说明、实现或原型、验证结果、问题复盘。"
        else:
            body = f"讲解脚本：{knowledge_point}\n\n依据片段：{source_title}\n\n讲解内容：\n{source_content}\n\n结尾提问：请说明该知识点在目标岗位中的使用条件和常见误区。"
        return {
            "content_type": resource_type,
            "title": title,
            "body": body,
            "difficulty": difficulty,
        }, hits


class PathAgent:
    name = "个性化学习路径 Agent"

    def run(self, user_id: str, target_job: str, current_ability: list[float], events: list[AgentEvent]) -> list[dict[str, Any]]:
        role = ROLE_PROFILES[target_job]
        values_by_dimension = {
            name: float(current_ability[index - 1]) if index - 1 < len(current_ability) else 0.18
            for index, name, _category in DIMENSIONS
        }
        candidates = []
        for skill, dimension in role["skills"]:
            candidates.append((values_by_dimension.get(dimension, 0.18), skill, dimension))
        candidates.sort(key=lambda item: item[0])
        selected = candidates[:6]
        steps: list[dict[str, Any]] = []
        previous = None
        for index, (value, skill, _dimension) in enumerate(selected, start=1):
            steps.append({
                "step": index,
                "knowledge_point": skill,
                "resource_type": "讲义" if index % 2 else "练习",
                "estimated_time": 30 if value < 0.45 else 20,
                "prerequisite": previous,
            })
            previous = skill
        events.append(AgentEvent(
            name=self.name,
            status="completed",
            input_summary=f"根据 {target_job} 的 16 维能力向量排序补强顺序。",
            output_summary=f"生成 {len(steps)} 个学习步骤。",
            confidence=0.82,
        ))
        return steps


class AgentRuntime:
    """Serial supervisor for all four jobs."""

    def __init__(self, retriever: Retriever | None = None):
        self.retriever = retriever or BackendVectorRetriever()
        self.last_trace: dict[str, Any] = {}
        self._current_job: ContextVar[str] = ContextVar("agent_current_job", default="后端开发工程师")

    def _role(self, target_job: str) -> str:
        role = normalize_job(target_job)
        if role not in ROLE_PROFILES:
            raise ValueError(f"不支持的目标职业：{target_job}")
        return role

    def diagnose(self, user_id: str, target_job: str, user_input: str) -> dict[str, Any]:
        role = self._role(target_job)
        self._current_job.set(role)
        trace_id = f"trace_{uuid4().hex[:12]}"
        events: list[AgentEvent] = []
        parser = InputParsingAgent()
        profile = parser.run(role, user_input)
        events.append(AgentEvent(
            name=parser.name,
            status="completed",
            input_summary="接收一段自由文本，不额外要求测评分数、每周学时或多字段资料提交。",
            output_summary=f"识别 {len(profile.matched_skills)} 个岗位关键词，发现 {len(profile.negative_skills)} 个否定表述。",
            confidence=0.84 if len(profile.text) >= 30 else 0.58,
        ))
        RAGEvidenceAgent(self.retriever).run(role, profile, events)
        diagnosis = CapabilityScoringAgent().run(role, profile, events)
        diagnosis = CalibrationAgent().run(diagnosis, profile, events)
        self.last_trace = self._trace(trace_id, user_id, role, events, profile, diagnosis, None)
        return diagnosis

    def generate_resource(self, knowledge_point: str, user_level: float, resource_type: str) -> dict[str, Any]:
        role = self._current_job.get()
        if role not in ROLE_PROFILES:
            role = "后端开发工程师"
        events: list[AgentEvent] = []
        resource, hits = ResourceAgent(self.retriever).run(knowledge_point, user_level, resource_type, role)
        events.append(AgentEvent(
            name=ResourceAgent.name,
            status="completed" if hits else "blocked",
            input_summary=f"针对 {role} 的“{knowledge_point}”生成{resource_type}。",
            output_summary="已绑定现有岗位知识库片段。" if hits else "没有知识库来源，禁止生成正式内容。",
            confidence=0.86 if hits else 0.15,
            review_result="approved" if hits else "blocked",
        ))
        self.last_trace = {
            "trace_id": f"trace_{uuid4().hex[:12]}",
            "target_job": role,
            "agents": [event.__dict__ for event in events],
            "retrieval_sources": hits,
            "review": {"approved": bool(hits), "errors": [] if hits else ["知识库无可用来源"]},
        }
        return resource

    def plan_learning_path(self, user_id: str, target_job: str, current_ability: list[float]) -> list[dict[str, Any]]:
        role = self._role(target_job)
        self._current_job.set(role)
        events: list[AgentEvent] = []
        steps = PathAgent().run(user_id, role, current_ability, events)
        self.last_trace = {
            "trace_id": f"trace_{uuid4().hex[:12]}",
            "target_job": role,
            "agents": [event.__dict__ for event in events],
            "review": {"approved": True, "errors": []},
        }
        return steps

    def _trace(self, trace_id: str, user_id: str, role: str, events: list[AgentEvent], profile: ParsedProfile, diagnosis: dict[str, Any], hits: Any) -> dict[str, Any]:
        return {
            "trace_id": trace_id,
            "user_id": user_id,
            "target_job": role,
            "agents": [event.__dict__ for event in events],
            "matched_skills": profile.matched_skills,
            "negative_skills": sorted(profile.negative_skills),
            "retrieval_sources": profile.retrieval_hits if hits is None else hits,
            "diagnosis": diagnosis,
            "review": {"approved": True, "errors": []},
        }


def _contains_skill(text: str, skill: str) -> bool:
    if skill.lower() in text.lower():
        return True
    aliases = {
        "JavaScript": ["js"], "TypeScript": ["ts"], "Spring Boot": ["springboot"],
        "MySQL": ["mysql", "sql"], "Kubernetes": ["k8s"], "CI/CD": ["cicd"],
        "Webpack/Vite": ["webpack", "vite"], "API设计": ["api", "接口"],
        "用户研究": ["用户调研"], "文档撰写": ["prd", "需求文档"],
        "网络协议": ["tcp", "http", "dns"], "安全编码": ["安全", "权限"],
    }
    return any(alias.lower() in text.lower() for alias in aliases.get(skill, []))


def _skill_context(text: str, skill: str, window: int = 42) -> str:
    lowered = text.lower()
    needles = [skill.lower()]
    aliases = {"JavaScript": ["js"], "MySQL": ["sql"], "Spring Boot": ["springboot"], "Kubernetes": ["k8s"]}
    needles.extend(aliases.get(skill, []))
    for needle in needles:
        index = lowered.find(needle)
        if index >= 0:
            return text[max(0, index - window): index + len(needle) + window]
    return text


def _is_negative_claim(text: str, skill: str) -> bool:
    context = _skill_context(text, skill)
    return bool(re.search(r"不会|不熟|没学过|未接触|不了解|没做过|不懂|未掌握", context, flags=re.IGNORECASE))

