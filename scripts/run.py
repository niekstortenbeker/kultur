"""
command line interface for Kultur
"""

import click
import program


@click.command()
@click.option(
    "-n",
    "--new",
    is_flag=True,
    help="Scrape websites to make a new database. (Otherwise start from old database)",
)
@click.option("-t", "--today", is_flag=True, help="Show only today")
def main(new, today):
    """Collect the program of theaters I like in bremen.
    It filters out dubbed movies (because who likes those?), and then
    combines the programs to one sorted-by-date overview.
    """
    p = program.CombinedProgram()
    print_header()
    if new:
        p.update_program()

    if today:
        p.program.print_today()
    else:
        p.program.print_next_week()


def print_header():
    print("".center(100, "-"))
    print("Kultur Factory".center(100, " "))
    print("".center(100, "-"))


if __name__ == "__main__":
    main()
