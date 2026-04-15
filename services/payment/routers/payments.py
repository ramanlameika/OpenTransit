import secrets
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Payment, PaymentStatus
from schemas import PaymentCreate, PaymentOut

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(payment_in: PaymentCreate, db: Session = Depends(get_db)):
    payment = Payment(
        ticket_id=payment_in.ticket_id,
        user_id=payment_in.user_id,
        amount=payment_in.amount,
        currency=payment_in.currency,
        status=PaymentStatus.completed,
        gateway_ref=secrets.token_hex(16),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("", response_model=List[PaymentOut])
def list_payments(
    user_id: Optional[str] = None,
    status: Optional[PaymentStatus] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Payment)
    if user_id:
        query = query.filter(Payment.user_id == user_id)
    if status:
        query = query.filter(Payment.status == status)
    return query.all()


@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: str, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.post("/{payment_id}/refund", response_model=PaymentOut)
def refund_payment(payment_id: str, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status != PaymentStatus.completed:
        raise HTTPException(status_code=400, detail="Payment cannot be refunded")
    payment.status = PaymentStatus.refunded
    payment.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(payment)
    return payment
