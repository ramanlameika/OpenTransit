import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
import enum


class TicketStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    used = "used"
    cancelled = "cancelled"
    expired = "expired"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    route_id: Mapped[str] = mapped_column(String(36), nullable=False)
    status: Mapped[str] = mapped_column(SAEnum(TicketStatus), nullable=False, default=TicketStatus.active)
    fare: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    qr_code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
