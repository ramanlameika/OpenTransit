from datetime import datetime, timezone
from typing import Optional
import uuid

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Agency Service", version="1.0.0")

# In-memory stores
agencies_db: dict[str, dict] = {}
routes_db: dict[str, dict] = {}  # route_id -> route dict
agency_routes_index: dict[str, list[str]] = {}  # agency_id -> list of route_ids


class CreateAgencyRequest(BaseModel):
    name: str
    region: str
    contact_email: str


class AgencyResponse(BaseModel):
    id: str
    name: str
    region: str
    contact_email: str
    created_at: str


class RouteResponse(BaseModel):
    id: str
    agency_id: str
    name: str
    origin: str
    destination: str
    created_at: str


class CreateRouteRequest(BaseModel):
    name: str
    origin: str
    destination: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "agency"}


@app.get("/agencies", response_model=list[AgencyResponse])
def list_agencies():
    return list(agencies_db.values())


@app.post("/agencies", response_model=AgencyResponse, status_code=status.HTTP_201_CREATED)
def create_agency(body: CreateAgencyRequest):
    agency = {
        "id": str(uuid.uuid4()),
        "name": body.name,
        "region": body.region,
        "contact_email": body.contact_email,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    agencies_db[agency["id"]] = agency
    agency_routes_index[agency["id"]] = []
    return agency


@app.get("/agencies/{agency_id}", response_model=AgencyResponse)
def get_agency(agency_id: str):
    agency = agencies_db.get(agency_id)
    if not agency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agency not found")
    return agency


@app.get("/agencies/{agency_id}/routes", response_model=list[RouteResponse])
def list_agency_routes(agency_id: str):
    if agency_id not in agencies_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agency not found")
    route_ids = agency_routes_index.get(agency_id, [])
    return [routes_db[rid] for rid in route_ids]
