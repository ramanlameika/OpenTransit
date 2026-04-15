import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Ticket, TicketStatus
from schemas import TicketCreate, TicketOut

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def issue_ticket(ticket_in: TicketCreate, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    ticket = Ticket(
        user_id=ticket_in.user_id,
        route_id=ticket_in.route_id,
        fare=ticket_in.fare,
        qr_code=secrets.token_hex(32),
        issued_at=now,
        expires_at=now + timedelta(hours=24),
        status=TicketStatus.active,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("", response_model=List[TicketOut])
def list_tickets(
    user_id: Optional[str] = None,
    status: Optional[TicketStatus] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Ticket)
    if user_id:
        query = query.filter(Ticket.user_id == user_id)
    if status:
        query = query.filter(Ticket.status == status)
    return query.all()


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("/{ticket_id}/validate", response_model=TicketOut)
def validate_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.status != TicketStatus.active:
        raise HTTPException(status_code=400, detail="Ticket cannot be validated")
    expires_at = ticket.expires_at if ticket.expires_at.tzinfo else ticket.expires_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        ticket.status = TicketStatus.expired
        db.commit()
        raise HTTPException(status_code=400, detail="Ticket has expired")
    ticket.status = TicketStatus.used
    ticket.used_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.post("/{ticket_id}/cancel", response_model=TicketOut)
def cancel_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.status not in (TicketStatus.pending, TicketStatus.active):
        raise HTTPException(status_code=400, detail="Ticket cannot be cancelled")
    ticket.status = TicketStatus.cancelled
    db.commit()
    db.refresh(ticket)
    return ticket
