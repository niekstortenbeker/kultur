from typing import List

import emoji
from colorama import Back, Fore, Style, init
from kultur.data.show import Show

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

    last_day = ""
    for show in program:
        if last_day != show.day:
            _print_day_separator(show.day)
            last_day = show.day
        _print_show(show)


def _print_update_date(program: List[Show]):
    most_recent_update = max(show.creation_date for show in program)
    print(
        f"\nThe most recent update to this program was {most_recent_update.humanize()}"
    )


def _print_day_separator(day: str):
    print_message = f"{Style.BRIGHT} {day} ".center(50, "-")
    print(f"\n{print_message}\n")


def _print_show(show: Show):
    """print information about one show on one line"""
    c1, c2, stop = _get_styles(show.location)
    description = show.description_start if show.description_start else ""
    print(f"{Style.BRIGHT}{show.time}{stop} | ", end="")
    print(f"{c1}{show.location}{stop} | ", end="")
    print(f"{c2}{show.title}{stop} | ", end="")
    print(f"{show.url_info} |", end="")
    print(f"{description}\n", end="")


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
