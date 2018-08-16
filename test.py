import CreateDatabase
import webscraping
import InputOutput
from pprint import pprint
import os


ostertor = webscraping.CinemaOstertor()
program = ostertor.create_program_db()
