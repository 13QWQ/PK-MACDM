"""
评估模块 - 创建评估、提交用户输入、查询结果
"""

import traceback
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.assessment import Assessment
from models.path import LearningPath
from models.resource import Resource
from models.job import Job
from models.user import User
from routers.auth import get_current_user
from adapters import agent_adapter

router = APIRouter()


# ===== 诊断进度（进程内，供前端轮询）=====
_PROGRESS: dict[str, dict] = {}   # assessment_id -> {"label": str, "percent": int}


def _set_progress(assessment_id: str, label: str, percent: int) -> None:
    """记录某次诊断的当前阶段进度"""
    _PROGRESS[assessment_id] = {"label": label, "percent": int(percent)}


# ===== 请求/响应模型 =====

class CreateAssessmentRequest(BaseModel):
    job_id: str


class SubmitAssessmentRequest(BaseModel):
    user_input: str  # 用户自由文本输入


class ReviewInputRequest(BaseModel):
    job_id: str
    user_input: str


class ReviewInputResponse(BaseModel):
    sufficient: bool
    missing: list[str]
    hint: str


class DimensionItem(BaseModel):
    """能力向量的单个维度"""
    index: int
    name: str
    value: float
    weight: Literal["high", "mid", "low"]
    category: str


class AssessmentResponse(BaseModel):
    id: str
    user_id: str
    job_id: str
    user_input: str | None = None
    overall_mastery: float | None = None
    ability_vector: list[DimensionItem] | None = None
    ability_matrix: list | None = None
    knowledge_gaps: list | None = None
    gap_validation: list | None = None
    confidence: float | None = None
    created_at: datetime


class DiagnosisResponse(BaseModel):
    overall_mastery: float
    ability_vector: list[DimensionItem]
    ability_matrix: list
    knowledge_gaps: list
    confidence: float


class AssessmentListItem(BaseModel):
    """评估历史列表项（轻量，不含ability_vector）"""
    id: str
    user_id: str
    job_id: str
    overall_mastery: float | None = None
    knowledge_gaps: list | None = None
    created_at: datetime


# ===== 接口 =====

@router.get("/list", response_model=list[AssessmentListItem])
def list_assessments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的评估历史，按创建时间倒序"""
    return (
        db.query(Assessment)
        .filter(Assessment.user_id == current_user.id)
        .order_by(Assessment.created_at.desc())
        .all()
    )


@router.post("/create", response_model=AssessmentResponse, status_code=201)
def create_assessment(
    request: CreateAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建评估"""
    assessment = Assessment(
        user_id=current_user.id,
        job_id=request.job_id,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return assessment


@router.post("/review-input", response_model=ReviewInputResponse)
def review_input(
    request: ReviewInputRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交前审查输入是否足以支撑诊断（宽松标准，判断不了放行）"""
    job = db.query(Job).filter(Job.id == request.job_id).first()
    target_job = job.job_title if job else ""
    from adapters.input_review import review_input as _review

    return _review(request.user_input, target_job)


@router.post("/{assessment_id}/submit", response_model=AssessmentResponse)
def submit_assessment(
    assessment_id: str,
    request: SubmitAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交用户自由文本输入"""
    # 查询评估
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id,
    ).first()

    if not assessment:
        raise HTTPException(status_code=404, detail="评估不存在")

    # 保存用户输入
    assessment.user_input = request.user_input
    db.commit()

    try:
        _set_progress(assessment.id, "正在解析学习情况", 5)

        # 从评估关联的岗位获取目标职业名称
        job = db.query(Job).filter(Job.id == assessment.job_id).first()
        target_job = job.job_title if job else ""

        # ① 调用诊断接口
        _set_progress(assessment.id, "正在能力诊断", 10)
        diagnosis = agent_adapter.diagnose(
            user_id=current_user.id,
            target_job=target_job,
            user_input=request.user_input,
        )
        _set_progress(assessment.id, "能力诊断完成", 45)

        print(f"[DEBUG] knowledge_gaps: {diagnosis.get('knowledge_gaps')}", flush=True)
        print(f"[DEBUG] overall_mastery: {diagnosis.get('overall_mastery')}", flush=True)
        print(f"[DEBUG] ability_vector count: {len(diagnosis.get('ability_vector', []))}", flush=True)

        # ② 更新评估结果
        assessment.overall_mastery = diagnosis["overall_mastery"]
        assessment.ability_vector = diagnosis["ability_vector"]
        assessment.ability_matrix = diagnosis.get("ability_matrix", [])
        assessment.knowledge_gaps = diagnosis["knowledge_gaps"]
        assessment.gap_validation = diagnosis.get("gap_validation", [])
        assessment.confidence = diagnosis["confidence"]

        # ③ 先生成学习路径（资源将按路径知识点生成，保证两边对齐）
        raw_vector = [item["value"] for item in diagnosis["ability_vector"]]
        _set_progress(assessment.id, "正在生成学习路径", 50)
        path_steps = agent_adapter.plan_learning_path(
            user_id=current_user.id,
            target_job=target_job,
            current_ability=raw_vector,
        )
        if path_steps:
            learning_path = LearningPath(
                user_id=current_user.id,
                job_id=assessment.job_id,
                steps=path_steps,
                current_step=1,
                status="active",
            )
            db.add(learning_path)

        # ④ 按路径的知识点生成资源（去重，每个知识点生成讲义+练习）
        seen_points = set()
        path_knowledge_points = []
        for s in path_steps:
            kp = s.get("knowledge_point", "")
            if kp and kp not in seen_points:
                seen_points.add(kp)
                path_knowledge_points.append(kp)

        resource_types = ["讲义", "练习"]
        generated_resources = []
        resource_by_id = {}
        total_resources = max(1, len(path_knowledge_points) * len(resource_types))
        generated_count = 0
        for i, gap in enumerate(path_knowledge_points):
            gap_id = f"gap_{i+1:03d}"
            for rtype in resource_types:
                generated = agent_adapter.generate_resource(
                    knowledge_point=gap,
                    user_level=diagnosis["overall_mastery"],
                    resource_type=rtype,
                    gap_id=gap_id,
                )
                resource = Resource(
                    knowledge_point=gap,
                    content_type=generated["content_type"],
                    title=generated["title"],
                    body=generated["body"],
                    difficulty=generated.get("difficulty"),
                    source_chunk_id=generated.get("source_chunk_id"),
                    source_text=generated.get("source_text"),
                    source_title=generated.get("source_title"),
                    source_score=generated.get("source_score"),
                )
                db.add(resource)
                resource_by_id[resource.id] = resource
                generated_resources.append({
                    "resource_id": resource.id,
                    "title": generated["title"],
                    "body": generated["body"],
                    "gap_id": generated.get("gap_id", gap_id),
                    "source_chunk_id": generated.get("source_chunk_id", ""),
                    "source_text": generated.get("source_text", ""),
                })
                generated_count += 1
                _set_progress(
                    assessment.id,
                    f"正在生成学习资源 ({generated_count}/{total_resources})",
                    55 + round(35 * generated_count / total_resources),
                )

        # ⑤ 内容审核（层2：逐条资源做知识库校验，防幻觉）
        _set_progress(assessment.id, "正在内容审查", 92)
        package_id = f"pkg_{assessment.id}"
        review_results = agent_adapter.review_resources(package_id, generated_resources)
        for rr in review_results:
            res = resource_by_id.get(rr.get("resource_id"))
            if res:
                res.review_status = rr.get("status")
                res.review_reason = rr.get("reason")

        # ⑤.5 完整性兜底：检查低分维度是否全部覆盖，缺失则补资源
        from adapters.agent_runtime import DIMENSIONS as _DIMS, ROLE_PROFILES as _ROLES
        _role = _ROLES.get(target_job, _ROLES["后端开发工程师"])
        # 构建 skill→dimension 映射
        _skill_to_dim = {s: d for s, d in _role["skills"]}
        # 路径已覆盖的维度
        _covered_dims = set()
        for _kp in path_knowledge_points:
            _dim = _skill_to_dim.get(_kp)
            if _dim:
                _covered_dims.add(_dim)
            else:
                # knowledge_point 可能是具体问题而非技能名，尝试模糊匹配
                for _skill, _dim2 in _skill_to_dim.items():
                    if _skill.lower() in _kp.lower() or any(kw.lower() in _kp.lower() for kw in _skill.lower().split()):
                        _covered_dims.add(_dim2)
                        break
        # 低分维度（<0.6）
        _low_dims = []
        for _item in diagnosis["ability_vector"]:
            if _item["value"] < 0.6:
                _low_dims.append(_item["name"])
        _missing = [d for d in _low_dims if d not in _covered_dims]
        if _missing:
            print(f"[CHECK] 低分维度缺失: {_missing}，自动补资源", flush=True)
            for _dim_name in _missing[:3]:  # 最多补 3 个
                # 找该维度下分数最低的技能
                _dim_skills = [(s, d) for s, d in _role["skills"] if d == _dim_name]
                if _dim_skills:
                    _skill_name = _dim_skills[0][0]
                    if _skill_name not in seen_points:
                        seen_points.add(_skill_name)
                        for rtype in resource_types:
                            generated = agent_adapter.generate_resource(
                                knowledge_point=_skill_name,
                                user_level=diagnosis["overall_mastery"],
                                resource_type=rtype,
                                gap_id=f"gap_fill_{_dim_name}",
                            )
                            resource = Resource(
                                knowledge_point=_skill_name,
                                content_type=generated["content_type"],
                                title=generated["title"],
                                body=generated["body"],
                                difficulty=generated.get("difficulty"),
                            )
                            db.add(resource)
        print(f"[CHECK] 覆盖维度: {len(_covered_dims)}/{len(_low_dims)} 低分维度, 资源总数: {len(generated_resources)}", flush=True)

        # ⑥ 持久化
        db.commit()
        db.refresh(assessment)
        _set_progress(assessment.id, "完成", 100)

        return assessment

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        db.rollback()
        _PROGRESS.pop(assessment_id, None)
        raise HTTPException(status_code=500, detail=f"诊断失败: {e}")


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询评估结果"""
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id,
    ).first()

    if not assessment:
        raise HTTPException(status_code=404, detail="评估不存在")

    return assessment


@router.get("/{assessment_id}/progress")
def get_progress(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询某次诊断的当前进度（供前端轮询）"""
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id,
    ).first()

    if not assessment:
        raise HTTPException(status_code=404, detail="评估不存在")

    return _PROGRESS.get(assessment_id, {"label": "正在解析学习情况", "percent": 0})


@router.get("/{assessment_id}/diagnosis", response_model=DiagnosisResponse)
def get_diagnosis(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询诊断报告"""
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id,
    ).first()

    if not assessment:
        raise HTTPException(status_code=404, detail="评估不存在")

    if not assessment.overall_mastery:
        raise HTTPException(status_code=400, detail="评估尚未完成")

    return {
        "overall_mastery": float(assessment.overall_mastery),
        "ability_vector": assessment.ability_vector,
        "ability_matrix": assessment.ability_matrix or [],
        "knowledge_gaps": assessment.knowledge_gaps,
        "confidence": float(assessment.confidence),
    }


@router.delete("/{assessment_id}")
def delete_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除评估记录"""
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id,
    ).first()

    if not assessment:
        raise HTTPException(status_code=404, detail="评估不存在")

    db.delete(assessment)
    db.commit()

    return {"message": "已删除"}
