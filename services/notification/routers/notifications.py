import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Notification, NotificationStatus
from schemas import NotificationCreate, NotificationOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("", response_model=NotificationOut, status_code=status.HTTP_201_CREATED)
def create_notification(notif_in: NotificationCreate, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    notification = Notification(
        user_id=notif_in.user_id,
        channel=notif_in.channel,
        subject=notif_in.subject,
        body=notif_in.body,
        status=NotificationStatus.sent,
        sent_at=now,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    logger.info(
        "[%s] Notification sent to user %s via %s: %s",
        notification.id,
        notification.user_id,
        notification.channel,
        notification.subject,
    )
    return notification


@router.get("", response_model=List[NotificationOut])
def list_notifications(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Notification)
    if user_id:
        query = query.filter(Notification.user_id == user_id)
    return query.all()


@router.get("/{notification_id}", response_model=NotificationOut)
def get_notification(notification_id: str, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification
