import webscraping
import CreateDatabase
import InputOutput
import time
from pprint import pprint

webscraping.start_driver()

try:
    filmkunst = webscraping.Filmkunst()
    program = filmkunst.create_program_db()#
finally:
    webscraping.close_driver()

