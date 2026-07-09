import enum
from sqlalchemy import Column, String, DateTime, Text, Integer, Enum
from sqlalchemy.sql import func
from .db import Base

class TaskStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    task_type = Column(String, index=True)
    topic = Column(String, index=True)
    platforms = Column(Text, default="[]")  # JSON string
    language = Column(String, default="en")
    timezone = Column(String, default="UTC")
    schedule_at = Column(String, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.queued, index=True)

    # Stage outputs
    research_output = Column(Text, nullable=True)   # JSON string
    script_output = Column(Text, nullable=True)     # JSON string
    render_output = Column(Text, nullable=True)     # JSON string

    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SocialPlatform(str, enum.Enum):
    youtube = "youtube"
    tiktok = "tiktok"
    instagram = "instagram"

class SocialConnection(Base):
    __tablename__ = "social_connections"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    platform = Column(Enum(SocialPlatform), index=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    scopes = Column(Text, nullable=True)  # JSON string
    meta = Column(Text, nullable=True)    # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ApprovalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    failed = "failed"
    no_answer = "no_answer"

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(String, primary_key=True, index=True)
    task_id = Column(String, index=True)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.pending, index=True)
    video_url = Column(Text, nullable=True)
    call_id = Column(String, nullable=True, index=True)
    decision = Column(String, nullable=True)     # yes|no|unknown
    transcript = Column(Text, nullable=True)
    ended_reason = Column(String, nullable=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

class PublishStatus(str, enum.Enum):
    queued = "queued"
    posting = "posting"
    posted = "posted"
    failed = "failed"

class PublishJob(Base):
    __tablename__ = "publish_jobs"

    id = Column(String, primary_key=True, index=True)
    task_id = Column(String, index=True)
    platform = Column(String, index=True)  # "youtube"
    status = Column(Enum(PublishStatus), default=PublishStatus.queued, index=True)
    remote_id = Column(String, nullable=True)      # YouTube videoId
    remote_url = Column(Text, nullable=True)       # YouTube Link
    request_payload = Column(Text, nullable=True)  # JSON string
    response_payload = Column(Text, nullable=True) # JSON string
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
