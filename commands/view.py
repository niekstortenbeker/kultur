from view import data, display


def print_today():
    program = data.get_program_today()
    display.print_program(program)


def print_week():
    program = data.get_program_week()
    display.print_program(program)


def print_header():
    display.print_header()
