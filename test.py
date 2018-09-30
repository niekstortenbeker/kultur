import CreateDatabase
import webscraping
import InputOutput
from pprint import pprint
import os

webscraping.start_driver()
filmkunst = webscraping.Filmkunst()
meta = filmkunst.create_meta_db()
webscraping.close_driver()