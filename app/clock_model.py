from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.circular_schedule import CircularClockRing, ClockMark


@dataclass(frozen=True)
class ClockHandAngles:
    """
    Stores the calculated angles for the three analog clock hands.
    """

    hour_angle: float
    minute_angle: float
    second_angle: float


class ClockEngine:
    """
    Contains the programming logic of the analog clock.

    This class calculates the angle of each hand and connects
    the clock with the circular doubly linked list structure.
    """

    def __init__(self) -> None:
        self.minute_ring = CircularClockRing.create_minute_ring()
        self.hour_ring = CircularClockRing.create_hour_ring()

    def calculate_hand_angles(self, current_time: Optional[datetime] = None) -> ClockHandAngles:
        selected_time = current_time or datetime.now()

        hour = selected_time.hour % 12
        minute = selected_time.minute
        second = selected_time.second

        hour_angle = (hour + minute / 60 + second / 3600) * 30.0
        minute_angle = (minute + second / 60) * 6.0
        second_angle = second * 6.0

        return ClockHandAngles(
            hour_angle=hour_angle,
            minute_angle=minute_angle,
            second_angle=second_angle
        )

    def get_current_minute_mark(self, current_time: Optional[datetime] = None) -> Optional[ClockMark]:
        selected_time = current_time or datetime.now()
        return self.minute_ring.find_by_value(selected_time.minute)

    def get_current_hour_mark(self, current_time: Optional[datetime] = None) -> Optional[ClockMark]:
        selected_time = current_time or datetime.now()

        hour_value = selected_time.hour % 12

        if hour_value == 0:
            hour_value = 12

        return self.hour_ring.find_by_value(hour_value)