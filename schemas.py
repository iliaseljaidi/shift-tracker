import datetime
from pydantic import BaseModel, ConfigDict, Field


class ShiftCreate(BaseModel):
    venue: str
    shift_date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    hourly_rate: float = Field(gt=0)
    notes: str | None = None


class ShiftOut(ShiftCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int