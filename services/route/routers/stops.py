from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Stop
from schemas import StopCreate, StopOut, StopUpdate

router = APIRouter(prefix="/stops", tags=["stops"])


@router.get("", response_model=List[StopOut])
def list_stops(db: Session = Depends(get_db)):
    return db.query(Stop).all()


@router.post("", response_model=StopOut, status_code=status.HTTP_201_CREATED)
def create_stop(stop_in: StopCreate, db: Session = Depends(get_db)):
    stop = Stop(**stop_in.model_dump())
    db.add(stop)
    db.commit()
    db.refresh(stop)
    return stop


@router.get("/{stop_id}", response_model=StopOut)
def get_stop(stop_id: str, db: Session = Depends(get_db)):
    stop = db.query(Stop).filter(Stop.id == stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    return stop


@router.put("/{stop_id}", response_model=StopOut)
def update_stop(stop_id: str, stop_in: StopUpdate, db: Session = Depends(get_db)):
    stop = db.query(Stop).filter(Stop.id == stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    for field, value in stop_in.model_dump(exclude_none=True).items():
        setattr(stop, field, value)
    db.commit()
    db.refresh(stop)
    return stop


@router.delete("/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stop(stop_id: str, db: Session = Depends(get_db)):
    stop = db.query(Stop).filter(Stop.id == stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    db.delete(stop)
    db.commit()
