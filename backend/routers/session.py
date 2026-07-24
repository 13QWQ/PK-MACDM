"""
会话模块 - 创建会话、查询消息列表
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from database import get_db
from models.session import Session
from models.user import User
from routers.auth import get_current_user

router = APIRouter()


# ===== 请求/响应模型 =====

class CreateSessionRequest(BaseModel):
    job_id: str


class SessionResponse(BaseModel):
    id: str
    user_id: str
    job_id: str
    status: str
    current_step: int
    progress: float
    started_at: datetime
    last_active_at: datetime


class MessageResponse(BaseModel):
    id: str
    role: str  # user 或 assistant
    content: str
    created_at: datetime


# ===== 接口 =====

@router.post("/create", response_model=SessionResponse, status_code=201)
def create_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    """创建学习会话"""
    session = Session(
        user_id=current_user.id,
        job_id=request.job_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return session


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    """查询会话详情"""
    session = db.query(Session).filter(
        Session.id == session_id,
        Session.user_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    return session


@router.get("/{session_id}/messages", response_model=list[MessageResponse])
def get_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    """查询会话消息列表"""
    # 验证会话存在且属于当前用户
    session = db.query(Session).filter(
        Session.id == session_id,
        Session.user_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # TODO: 消息表目前未定义，返回空列表
    # 后续可添加messages表，或从其他来源获取消息
    return []
