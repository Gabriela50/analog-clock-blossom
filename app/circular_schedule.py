from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional


@dataclass
class ClockMark:
    """
    Represents one mark of the analog clock.

    This class is used instead of a generic public Node class because
    the workshop requires professional names related to the project.
    """

    value: int
    label: str
    angle_degrees: float
    previous: Optional["ClockMark"] = None
    next: Optional["ClockMark"] = None


class CircularClockRing:
    """
    Circular doubly linked list used to represent the clock marks.

    Each mark has:
    - a previous reference
    - a next reference

    The last mark points again to the first mark.
    The first mark points back to the last mark.
    """

    def __init__(self) -> None:
        self._head: Optional[ClockMark] = None
        self._size: int = 0

    def append(self, value: int, label: str, angle_degrees: float) -> ClockMark:
        new_mark = ClockMark(
            value=value,
            label=label,
            angle_degrees=angle_degrees
        )

        if self._head is None:
            new_mark.next = new_mark
            new_mark.previous = new_mark
            self._head = new_mark
        else:
            last_mark = self._head.previous

            if last_mark is None:
                raise RuntimeError("The circular clock ring is broken.")

            new_mark.previous = last_mark
            new_mark.next = self._head

            last_mark.next = new_mark
            self._head.previous = new_mark

        self._size += 1
        return new_mark

    def find_by_value(self, value: int) -> Optional[ClockMark]:
        for mark in self.iter_forward():
            if mark.value == value:
                return mark

        return None

    def iter_forward(self) -> Iterator[ClockMark]:
        if self._head is None:
            return

        current_mark = self._head
        visited_marks = 0

        while visited_marks < self._size:
            yield current_mark

            if current_mark.next is None:
                return

            current_mark = current_mark.next
            visited_marks += 1

    def iter_backward(self) -> Iterator[ClockMark]:
        if self._head is None:
            return

        current_mark = self._head.previous

        if current_mark is None:
            return

        visited_marks = 0

        while visited_marks < self._size:
            yield current_mark

            if current_mark.previous is None:
                return

            current_mark = current_mark.previous
            visited_marks += 1

    def get_size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._head is None

    @classmethod
    def create_minute_ring(cls) -> "CircularClockRing":
        ring = cls()

        for minute in range(60):
            ring.append(
                value=minute,
                label=str(minute),
                angle_degrees=minute * 6.0
            )

        return ring

    @classmethod
    def create_hour_ring(cls) -> "CircularClockRing":
        ring = cls()

        for hour in range(1, 13):
            ring.append(
                value=hour,
                label=str(hour),
                angle_degrees=(hour % 12) * 30.0
            )

        return ring