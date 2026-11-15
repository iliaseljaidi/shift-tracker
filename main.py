from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import datetime
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

@app.put("/shifts/{shift_id}", response_model=schemas.ShiftOut)
def update_shift(shift_id: int, data: schemas.ShiftCreate, db: Session = Depends(get_db)):
    shift = db.get(models.Shift, shift_id)
    if shift is None:
        raise HTTPException(status_code=404, detail="Shift not found")
    for key, value in data.model_dump().items():
        setattr(shift, key, value)
    db.commit()
    db.refresh(shift)
    return shift

@app.delete("/shifts/{shift_id}", status_code=204)
def delete_shift(shift_id: int, db: Session = Depends(get_db)):
    shift = db.get(models.Shift, shift_id)
    if shift is None:
        raise HTTPException(status_code=404, detail="Shift not found")
    db.delete(shift)
    db.commit()

@app.get("/summary/weekly")
def weekly_summary(week_start: datetime.date, db: Session = Depends(get_db)):
    week_end = week_start + datetime.timedelta(days=7)
    shifts = (
        db.query(models.Shift)
        .filter(models.Shift.shift_date >= week_start,
                models.Shift.shift_date < week_end)
        .all()
    )
    outs = [schemas.ShiftOut.model_validate(s) for s in shifts]
    return {
        "week_start": week_start,
        "shifts": len(outs),
        "total_hours": round(sum(o.hours for o in outs), 2),
        "total_pay": round(sum(o.pay for o in outs), 2),
    }