"""
kultur - collect programs from a selection of theaters in Bremen
"""

__version__ = "0.2"
__author__ = "Niek Stortenbeker"

from kultur.commands.data import get_shows, init_database  # noqa
from kultur.commands.update import update_program  # noqa
from kultur.commands.view import print_header, print_today, print_week  # noqa
