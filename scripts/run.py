"""
command line interface for Kultur
"""

import click
import program


@click.command()
@click.option(
    "--new/--old",
    "-n",
    default=False,
    help="Scrape websites to make a new database. (Otherwise start from old database)",
)
@click.option("--today/--week", "-t", default=False, help="Only show today")
def main(new, today):
    p = program.CombinedProgram()
    print_header()
    if new:
        p.update_program()
    else:
        p.program_from_file()

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
