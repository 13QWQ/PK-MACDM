import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Numeric, ForeignKey

from database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    status = Column(String(20), default="active")  # active, paused, completed
    current_step = Column(Integer, default=1)
    progress = Column(Numeric(5, 4), default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
