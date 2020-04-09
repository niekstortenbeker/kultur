from typing import List

import arrow
import emoji
from colorama import Back, Fore, Style, init  # noqa: E402
from data.show import Show

init()


def print_header():
    print("-" * 100)
    statement = f"{38 * ' '}:movie_camera: Kultur Factory :movie_camera: "
    print(emoji.emojize(statement))
    print("-" * 100)


def print_program(program: List[Show]):
    if not program:  # empty programs
        print("There are no shows to display")
        return

    _print_update_date(program)

    last_date = arrow.get(0).date()  # a date that's always before the first show
    for show in program:
        if last_date != show.date_time.date():
            _print_day_separator(show.date_time)
            last_date = show.date_time.date()
        _print_show(show)


def _print_update_date(program):
    most_recent_update = max(show.date_time for show in program)
    print(
        f"\nThis program uses data that was most recently updated {most_recent_update.humanize()}"
    )


def _print_day_separator(date):
    print_message = f"{Style.BRIGHT} {date.format('dddd MM-DD')} ".center(50, "-")
    print(f"\n{print_message}\n")


def _print_show(show: Show):
    """print information about one show on one line"""
    c1, c2, stop = _get_styles(show.location)

    print(f"{Style.BRIGHT}{show.date_time.format('HH:mm')}{stop} | ", end="")
    print(f"{c1}{show.location}{stop} | ", end="")
    print(f"{c2}{show.title}{stop} | ", end="")
    print(f"{show.url_info} |", end="")
    print(f"{show.description}", end="")


def _get_styles(location: str):
    film_theaters = [
        "Schauburg",
        "Gondel",
        "Atlantis",
        "Cinema Ostertor",
        "City 46",
    ]
    if location in film_theaters:
        c1 = Back.LIGHTMAGENTA_EX
        c2 = Fore.MAGENTA
    else:
        c1 = Back.LIGHTBLUE_EX
        c2 = Fore.BLUE
    stop = Style.RESET_ALL
    return c1, c2, stop
