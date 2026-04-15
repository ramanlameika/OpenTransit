from datetime import datetime, timezone
from enum import Enum
import uuid

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Fare Service", version="1.0.0")

# In-memory store: fare_id -> fare dict
fares_db: dict[str, dict] = {}
# route_id -> list of fare_ids for fast lookup
route_fares_index: dict[str, list[str]] = {}


class FareType(str, Enum):
    standard = "standard"
    concession = "concession"
    child = "child"
    senior = "senior"


class CreateFareRequest(BaseModel):
    route_id: str
    fare_type: FareType
    amount: float

    model_config = {"json_schema_extra": {"example": {"route_id": "R1", "fare_type": "standard", "amount": 2.50}}}


class FareResponse(BaseModel):
    id: str
    route_id: str
    fare_type: FareType
    amount: float
    created_at: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "fare"}


@app.get("/fares", response_model=list[FareResponse])
def list_fares():
    return list(fares_db.values())


@app.post("/fares", response_model=FareResponse, status_code=status.HTTP_201_CREATED)
def create_fare(body: CreateFareRequest):
    if body.amount < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be non-negative")
    fare = {
        "id": str(uuid.uuid4()),
        "route_id": body.route_id,
        "fare_type": body.fare_type,
        "amount": body.amount,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    fares_db[fare["id"]] = fare
    route_fares_index.setdefault(body.route_id, []).append(fare["id"])
    return fare


@app.get("/fares/{route_id}", response_model=list[FareResponse])
def get_fares_for_route(route_id: str):
    fare_ids = route_fares_index.get(route_id, [])
    if not fare_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No fares found for route")
    return [fares_db[fid] for fid in fare_ids]
