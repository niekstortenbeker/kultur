import CreateDatabase
import webscraping
import output
from pprint import pprint
import os

webscraping.start_driver()

film = webscraping.Filmkunst()
test = film.get_meta_html('https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/movies?mode=widget')

webscraping.close_driver()