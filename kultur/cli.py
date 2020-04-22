"""
command line interface for Kultur
"""
import click
from kultur.commands import data, update, view


@click.command()
@click.option(
    "-n",
    "--new",
    is_flag=True,
    help="Scrape websites to make a new database. (Otherwise start from old database)",
)
@click.option("-t", "--display_today", is_flag=True, help="display only today")
def main(new, display_today):
    """Collect the program of theaters I like in bremen.
    It filters out dubbed movies (because who likes those?), and then
    combines the programs to one sorted-by-date overview.
    """

    run(new, display_today)


def run(new: bool, display_today: bool):
    """
    run the command line interface

    Parameters
    ----------
    new: bool
        if True update program first
    display_today: bool
        if True only print today, otherwise print next week
    """

    view.print_header()
    if new:
        update.update_program()
    print_program(display_today)


def print_program(display_today: bool):
    if display_today:
        view.print_today()
    else:
        view.print_week()


if __name__ == "__main__":
    data.init_database()
    main()
