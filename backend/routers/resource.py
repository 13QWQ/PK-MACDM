"""
资源模块 - 资源列表、资源详情
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.resource import Resource
from models.user import User
from routers.auth import get_current_user
from adapters import vector_adapter

router = APIRouter()


# ===== 响应模型 =====

class SearchResult(BaseModel):
    title: str
    content: str
    score: float
    source_chunk_id: str | None = None
    parent_source_chunk_id: str | None = None
    career_id: str | None = None


class SearchResponse(BaseModel):
    items: list[SearchResult]


class ResourceResponse(BaseModel):
    id: str
    knowledge_point: str
    content_type: str
    title: str
    body: str
    difficulty: int | None = None
    source_chunk_id: str | None = None
    source_text: str | None = None
    source_title: str | None = None
    source_score: float | None = None
    review_status: str | None = None
    review_reason: str | None = None
    generation_method: str | None = None
    display_status: str = "show"
    created_at: datetime


# ===== 接口 =====

@router.get("/search", response_model=SearchResponse)
def search_resources(
    q: str = Query(..., description="搜索关键词"),
    job: str = Query("产品经理", description="目标岗位"),
    top_k: int = Query(5, ge=1, le=20, description="返回条数"),
):
    """向量检索知识库"""
    items = vector_adapter.search_similar_resources(query=q, job=job, top_k=top_k)
    return {"items": items}


@router.get("/list", response_model=list[ResourceResponse])
def list_resources(
    knowledge_point: str | None = Query(None, description="按知识点过滤"),
    type: str | None = Query(None, alias="type", description="按资源类型过滤（讲义/练习/案例/视频脚本）"),
    assessment_id: str | None = Query(None, description="按诊断记录过滤"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取资源列表，支持按知识点/类型/诊断记录过滤，按创建时间倒序"""
    q = db.query(Resource)

    if knowledge_point:
        q = q.filter(Resource.knowledge_point == knowledge_point)
    if type:
        q = q.filter(Resource.content_type == type)
    if assessment_id:
        q = q.filter(Resource.assessment_id == assessment_id)

    return q.order_by(Resource.created_at.desc()).all()


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询资源详情"""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()

    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")

    return resource
