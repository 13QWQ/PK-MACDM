import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, Integer

from database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    knowledge_point = Column(String(100), nullable=False, index=True)
    content_type = Column(String(20), nullable=False)  # 讲义, 练习, 案例, 视频脚本
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    difficulty = Column(Integer, nullable=True)  # 1-5
    created_at = Column(DateTime, default=datetime.utcnow)
