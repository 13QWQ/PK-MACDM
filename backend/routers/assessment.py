"""
评估模块 - 创建评估、提交用户输入、查询结果
"""

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


# ===== 请求/响应模型 =====

class CreateAssessmentRequest(BaseModel):
    job_id: str


class SubmitAssessmentRequest(BaseModel):
    user_input: str  # 用户自由文本输入


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
    knowledge_gaps: list | None = None
    confidence: float | None = None
    created_at: datetime


class DiagnosisResponse(BaseModel):
    overall_mastery: float
    ability_vector: list[DimensionItem]
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

    # 从评估关联的岗位获取目标职业名称
    job = db.query(Job).filter(Job.id == assessment.job_id).first()
    target_job = job.job_title if job else ""

    # 调用诊断接口
    diagnosis = agent_adapter.diagnose(
        user_id=current_user.id,
        target_job=target_job,
        user_input=request.user_input,
    )

    # 更新评估结果
    assessment.overall_mastery = diagnosis["overall_mastery"]
    assessment.ability_vector = diagnosis["ability_vector"]
    assessment.knowledge_gaps = diagnosis["knowledge_gaps"]
    assessment.confidence = diagnosis["confidence"]

    # 根据薄弱知识点自动生成学习资源
    resource_types = ["讲义", "练习"]
    for gap in diagnosis["knowledge_gaps"]:
        for rtype in resource_types:
            generated = agent_adapter.generate_resource(
                knowledge_point=gap,
                user_level=diagnosis["overall_mastery"],
                resource_type=rtype,
            )
            resource = Resource(
                knowledge_point=gap,
                content_type=generated["content_type"],
                title=generated["title"],
                body=generated["body"],
                difficulty=generated.get("difficulty"),
            )
            db.add(resource)

    # 根据诊断结果自动生成学习路径
    raw_vector = [item["value"] for item in diagnosis["ability_vector"]]
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

    db.commit()
    db.refresh(assessment)

    return assessment


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
