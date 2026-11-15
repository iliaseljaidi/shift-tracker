import datetime


def shift_hours(start: datetime.time, end: datetime.time) -> float:
    start_min = start.hour * 60 + start.minute
    end_min = end.hour * 60 + end.minute
    if end_min <= start_min:
        end_min += 24 * 60
    return (end_min - start_min) / 60