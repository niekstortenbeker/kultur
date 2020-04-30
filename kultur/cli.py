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
@click.option(
    "-f", "--fake_data", is_flag=True, help="populate database with fake data"
)
def main(new, display_today, fake_data):
    """Collect the program of theaters I like in bremen.
    It filters out dubbed movies (because who likes those?), and then
    combines the programs to one sorted-by-date overview.
    """
    data.init_database()
    if fake_data:
        fake_data_to_database()
    else:
        run(new, display_today)


def fake_data_to_database():
    data.fake_data()
    print("populated the database with fake data!")
    print("run kultur -n to repopulate with real data")


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
