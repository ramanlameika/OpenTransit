from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from models import PaymentStatus


class PaymentCreate(BaseModel):
    ticket_id: str
    user_id: str
    amount: Decimal
    currency: str = "USD"


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_id: str
    user_id: str
    amount: Decimal
    currency: str
    status: PaymentStatus
    gateway_ref: Optional[str] = None
    created_at: datetime
    updated_at: datetime
