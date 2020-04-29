from typing import List, Tuple

import arrow
from arrow import Arrow
from kultur.data.show import Show
from kultur.data.showsgetter import ShowsGetter


def get_program_today() -> List[Show]:
    start, stop = start_and_stop_times(1)
    sg = ShowsGetter(start, stop)
    return sg.get()


def get_program_week() -> List[Show]:
    start, stop = start_and_stop_times(7)
    sg = ShowsGetter(start, stop)
    return sg.get()


def start_and_stop_times(number_of_days: int) -> Tuple[Arrow, Arrow]:
    start = arrow.now("Europe/Berlin")
    stop = start.shift(days=+number_of_days).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return start, stop
