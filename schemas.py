import datetime
from pydantic import BaseModel, ConfigDict, Field, computed_field
from calc import shift_hours


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

    @computed_field
    @property
    def hours(self) -> float:
        return round(shift_hours(self.start_time, self.end_time), 2)

    @computed_field
    @property
    def pay(self) -> float:
        return round(self.hours * self.hourly_rate, 2)