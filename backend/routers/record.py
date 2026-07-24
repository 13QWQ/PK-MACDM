"""
学习记录模块 - 创建记录、标记完成
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.learning_record import LearningRecord
from models.user import User
from routers.auth import get_current_user

router = APIRouter()


# ===== 请求/响应模型 =====

class CreateRecordRequest(BaseModel):
    session_id: str
    resource_id: str


class CompleteRecordRequest(BaseModel):
    score: float | None = None
    time_spent: int | None = None  # 秒


class RecordResponse(BaseModel):
    id: str
    user_id: str
    session_id: str
    resource_id: str
    status: str
    score: float | None = None
    time_spent: int
    started_at: datetime | None = None
    completed_at: datetime | None = None


# ===== 接口 =====

@router.post("/create", response_model=RecordResponse, status_code=201)
def create_record(
    request: CreateRecordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建学习记录（开始学习某个资源）"""
    record = LearningRecord(
        user_id=current_user.id,
        session_id=request.session_id,
        resource_id=request.resource_id,
        status="in_progress",
        started_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.put("/{record_id}/complete", response_model=RecordResponse)
def complete_record(
    record_id: str,
    request: CompleteRecordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """标记学习记录为已完成"""
    record = db.query(LearningRecord).filter(
        LearningRecord.id == record_id,
        LearningRecord.user_id == current_user.id,
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="学习记录不存在")

    record.status = "completed"
    record.completed_at = datetime.utcnow()

    if request.score is not None:
        record.score = request.score
    if request.time_spent is not None:
        record.time_spent = request.time_spent

    db.commit()
    db.refresh(record)

    return record
