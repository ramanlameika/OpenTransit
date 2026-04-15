from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Ticketing Service", version="1.0.0")

# In-memory store
tickets_db: dict[str, dict] = {}


class TicketType(str, Enum):
    single = "single"
    day_pass = "day_pass"
    weekly = "weekly"
    monthly = "monthly"


class TicketStatus(str, Enum):
    active = "active"
    validated = "validated"
    expired = "expired"
    cancelled = "cancelled"


class CreateTicketRequest(BaseModel):
    route_id: str
    passenger_id: str
    ticket_type: TicketType


class TicketResponse(BaseModel):
    id: str
    route_id: str
    passenger_id: str
    ticket_type: TicketType
    status: TicketStatus
    created_at: str
    validated_at: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok", "service": "ticketing"}


@app.get("/tickets", response_model=list[TicketResponse])
def list_tickets():
    return list(tickets_db.values())


@app.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(body: CreateTicketRequest):
    ticket = {
        "id": str(uuid.uuid4()),
        "route_id": body.route_id,
        "passenger_id": body.passenger_id,
        "ticket_type": body.ticket_type,
        "status": TicketStatus.active,
        "created_at": datetime.utcnow().isoformat(),
        "validated_at": None,
    }
    tickets_db[ticket["id"]] = ticket
    return ticket


@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str):
    ticket = tickets_db.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@app.post("/tickets/{ticket_id}/validate", response_model=TicketResponse)
def validate_ticket(ticket_id: str):
    ticket = tickets_db.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    if ticket["status"] != TicketStatus.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticket cannot be validated (status: {ticket['status']})",
        )
    ticket["status"] = TicketStatus.validated
    ticket["validated_at"] = datetime.utcnow().isoformat()
    return ticket
