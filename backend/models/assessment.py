import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, JSON, Numeric, Text, ForeignKey

from database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    user_input = Column(Text, nullable=True)  # 用户自由文本输入
    overall_mastery = Column(Numeric(5, 4), nullable=True)
    ability_vector = Column(JSON, nullable=True)  # 16个维度的值
    knowledge_gaps = Column(JSON, nullable=True)  # 薄弱知识点
    confidence = Column(Numeric(5, 4), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
