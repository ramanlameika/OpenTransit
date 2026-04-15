from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from models import NotificationChannel, NotificationStatus


class NotificationCreate(BaseModel):
    user_id: str
    channel: NotificationChannel
    subject: str
    body: str


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    channel: NotificationChannel
    subject: str
    body: str
    status: NotificationStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
