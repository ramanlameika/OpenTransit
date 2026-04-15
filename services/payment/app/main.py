from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Payment Service", version="1.0.0")

# In-memory store
payments_db: dict[str, dict] = {}


class PaymentMethod(str, Enum):
    card = "card"
    wallet = "wallet"
    bank_transfer = "bank_transfer"


class PaymentStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class CreatePaymentRequest(BaseModel):
    ticket_id: str
    amount: float
    method: PaymentMethod


class PaymentResponse(BaseModel):
    id: str
    ticket_id: str
    amount: float
    method: PaymentMethod
    status: PaymentStatus
    created_at: str
    refunded_at: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok", "service": "payment"}


@app.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(body: CreatePaymentRequest):
    if body.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")
    payment = {
        "id": str(uuid.uuid4()),
        "ticket_id": body.ticket_id,
        "amount": body.amount,
        "method": body.method,
        "status": PaymentStatus.completed,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "refunded_at": None,
    }
    payments_db[payment["id"]] = payment
    return payment


@app.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: str):
    payment = payments_db.get(payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment


@app.post("/payments/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(payment_id: str):
    payment = payments_db.get(payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    if payment["status"] == PaymentStatus.refunded:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment already refunded")
    if payment["status"] != PaymentStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot refund payment with status: {payment['status']}",
        )
    payment["status"] = PaymentStatus.refunded
    payment["refunded_at"] = datetime.now(timezone.utc).isoformat()
    return payment
