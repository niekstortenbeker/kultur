import webscraping
import CreateDatabase
import InputOutput
import time
from pprint import pprint

# webscraping.start_driver()
#
# try:
#     # filmkunst = webscraping.Filmkunst()
#     # filmkunst.update_program()
#     # print(filmkunst.create_meta_db())
#     # city46 = webscraping.City46()
#     # city46.update_program()
#     ostertor = webscraping.CinemaOstertor()
#     # ostertor.update_program()
#     print(ostertor.create_meta_db())
#     # theater_bremen = webscraping.TheaterBremen()
#     # theater_bremen.update_program()
#     # filmkunst = webscraping.Filmkunst()
#     # filmkunst.update_program()
#     # schwankhalle = webscraping.Schwankhalle()
#     # schwankhalle.update_program()
#     # kukoon = webscraping.Kukoon()
#     # kukoon.update_program()
#     # glocke = webscraping.Glocke()
#     # glocke = glocke.update_program()
# finally:
#     webscraping.close_driver()

p = webscraping.CombinedProgram()
print([t.program for t in p.theaters])
print(p.program)
p.update_program()
print([t.program for t in p.theaters])
print(p.theaters[0].program.shows[0].title)
print(p.program)
print(len(p.program.shows))
print(p.program.shows[0].title)

