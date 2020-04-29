from kultur.view import data, display


def print_today():
    """
    Print today's program.

    The program will be obtained from the database.
    """
    program = data.get_program_today()
    display.print_program(program)


def print_week():
    """
    Print the program one week ahead.

    The program will be obtained from the database.
    """
    program = data.get_program_week()
    display.print_program(program)


def print_header():
    """print a "Kultur Factory" header"""
    display.print_header()
