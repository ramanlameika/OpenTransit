from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from models import TicketStatus


class TicketCreate(BaseModel):
    user_id: str
    route_id: str
    fare: Decimal


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    route_id: str
    status: TicketStatus
    fare: Decimal
    qr_code: str
    issued_at: datetime
    expires_at: datetime
    used_at: Optional[datetime] = None
