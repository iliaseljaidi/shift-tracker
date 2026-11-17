
import datetime
from calc import shift_hours


def test_normal_shift():
    assert shift_hours(datetime.time(9, 0), datetime.time(17, 0)) == 8


def test_overnight_shift():
    assert shift_hours(datetime.time(22, 0), datetime.time(4, 0)) == 6


def test_half_hours():
    assert shift_hours(datetime.time(18, 30), datetime.time(23, 0)) == 4.5
