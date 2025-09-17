from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class JobStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class JobModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    metadata: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class AddJob(BaseModel):
    status: str = JobStatus.PENDING
    metadata: Optional[str] = None


class UpdateJobStatus(BaseModel):
    status: str
