import CreateDatabase
import webscraping
import InputOutput
from pprint import pprint
import os
import bs4


webscraping.start_driver()

try:
    ostertor = webscraping.CinemaOstertor()
    program = ostertor.create_program_db()
    meta = ostertor.create_meta_db()
    print(program)
    print(meta)
finally:
    webscraping.close_driver()


