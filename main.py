from fastapi.security import OAuth2PasswordRequestForm
import auth
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import datetime
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shift Tracker")


def get_own_shift(db: Session, shift_id: int, user: models.User) -> models.Shift:
    shift = db.get(models.Shift, shift_id)
    if shift is None or shift.user_id != user.id:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift


@app.post("/shifts", response_model=schemas.ShiftOut, status_code=201)
def create_shift(shift: schemas.ShiftCreate, db: Session = Depends(get_db),
                 user: models.User = Depends(auth.get_current_user)):
    db_shift = models.Shift(**shift.model_dump(), user_id=user.id)
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return db_shift


@app.get("/shifts", response_model=list[schemas.ShiftOut])
def list_shifts(db: Session = Depends(get_db),
                user: models.User = Depends(auth.get_current_user)):
    return (db.query(models.Shift)
            .filter(models.Shift.user_id == user.id)
            .order_by(models.Shift.shift_date.desc())
            .all())


@app.get("/shifts/{shift_id}", response_model=schemas.ShiftOut)
def get_shift(shift_id: int, db: Session = Depends(get_db),
              user: models.User = Depends(auth.get_current_user)):
    return get_own_shift(db, shift_id, user)


@app.put("/shifts/{shift_id}", response_model=schemas.ShiftOut)
def update_shift(shift_id: int, data: schemas.ShiftCreate,
                 db: Session = Depends(get_db),
                 user: models.User = Depends(auth.get_current_user)):
    shift = get_own_shift(db, shift_id, user)
    for key, value in data.model_dump().items():
        setattr(shift, key, value)
    db.commit()
    db.refresh(shift)
    return shift


@app.delete("/shifts/{shift_id}", status_code=204)
def delete_shift(shift_id: int, db: Session = Depends(get_db),
                 user: models.User = Depends(auth.get_current_user)):
    shift = get_own_shift(db, shift_id, user)
    db.delete(shift)
    db.commit()


@app.get("/summary/weekly")
def weekly_summary(week_start: datetime.date, db: Session = Depends(get_db),
                   user: models.User = Depends(auth.get_current_user)):
    week_end = week_start + datetime.timedelta(days=7)
    shifts = (
        db.query(models.Shift)
        .filter(models.Shift.user_id == user.id,
                models.Shift.shift_date >= week_start,
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

@app.post("/register", status_code=201)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(email=data.email,
                       password_hash=auth.hash_password(data.password))
    db.add(user)
    db.commit()
    return {"message": "Account created"}


@app.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if user is None or not auth.verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    return {"access_token": auth.create_token(user.id), "token_type": "bearer"}
