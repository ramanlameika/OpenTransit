from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Route, RouteStop, Stop
from schemas import RouteCreate, RouteOut, RouteUpdate, RouteStopCreate, RouteStopOut

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("", response_model=List[RouteOut])
def list_routes(db: Session = Depends(get_db)):
    return db.query(Route).all()


@router.post("", response_model=RouteOut, status_code=status.HTTP_201_CREATED)
def create_route(route_in: RouteCreate, db: Session = Depends(get_db)):
    route = Route(**route_in.model_dump())
    db.add(route)
    db.commit()
    db.refresh(route)
    return route


@router.get("/{route_id}", response_model=RouteOut)
def get_route(route_id: str, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.put("/{route_id}", response_model=RouteOut)
def update_route(route_id: str, route_in: RouteUpdate, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    for field, value in route_in.model_dump(exclude_none=True).items():
        setattr(route, field, value)
    db.commit()
    db.refresh(route)
    return route


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(route_id: str, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    db.delete(route)
    db.commit()


@router.get("/{route_id}/stops", response_model=List[RouteStopOut])
def get_route_stops(route_id: str, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return (
        db.query(RouteStop)
        .filter(RouteStop.route_id == route_id)
        .order_by(RouteStop.sequence)
        .all()
    )


@router.post("/{route_id}/stops", response_model=RouteStopOut, status_code=status.HTTP_201_CREATED)
def add_stop_to_route(route_id: str, rs_in: RouteStopCreate, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    stop = db.query(Stop).filter(Stop.id == rs_in.stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    rs = RouteStop(route_id=route_id, stop_id=rs_in.stop_id, sequence=rs_in.sequence)
    db.add(rs)
    db.commit()
    db.refresh(rs)
    return rs


@router.delete("/{route_id}/stops/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_stop_from_route(route_id: str, stop_id: str, db: Session = Depends(get_db)):
    rs = (
        db.query(RouteStop)
        .filter(RouteStop.route_id == route_id, RouteStop.stop_id == stop_id)
        .first()
    )
    if not rs:
        raise HTTPException(status_code=404, detail="RouteStop not found")
    db.delete(rs)
    db.commit()
