from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shift Tracker")


@app.post("/shifts", response_model=schemas.ShiftOut, status_code=201)
def create_shift(shift: schemas.ShiftCreate, db: Session = Depends(get_db)):
    db_shift = models.Shift(**shift.model_dump())
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return db_shift

@app.get("/shifts", response_model=list[schemas.ShiftOut])
def list_shifts(db: Session = Depends(get_db)):
    return db.query(models.Shift).order_by(models.Shift.shift_date.desc()).all()


@app.get("/shifts/{shift_id}", response_model=schemas.ShiftOut)
def get_shift(shift_id: int, db: Session = Depends(get_db)):
    shift = db.get(models.Shift, shift_id)
    if shift is None:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift