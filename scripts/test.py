import webscraping
import CreateDatabase
import InputOutput
import time
from pprint import pprint

webscraping.start_driver()

try:
    # filmkunst = webscraping.Filmkunst()
    # filmkunst.update_program()
    # city46 = webscraping.City46()
    # city46.update_program()
    ostertor = webscraping.CinemaOstertor()
    # ostertor.update_program()
    ostertor.update_meta_info()
    print(ostertor.meta_info)
    # theater_bremen = webscraping.TheaterBremen()
    # theater_bremen.update_program()
    # filmkunst = webscraping.Filmkunst()
    # filmkunst.update_program()
    # schwankhalle = webscraping.Schwankhalle()
    # schwankhalle.update_program()
    # kukoon = webscraping.Kukoon()
    # kukoon.update_program()
    # glocke = webscraping.Glocke()
    # glocke = glocke.update_program()
finally:
    webscraping.close_driver()


# p = webscraping.CombinedProgram()
# print(f'program / theater: {[t.program for t in p.theaters]}')
# print(f'combined program: {p.program}')
# p.update_program()
#
# program = [t.program for t in p.theaters]
# print(f'program / theater: {program}')
# length = [len(p.shows) for p in program]
# print(sum(length))
# print(f'combined program: {p.program}')
# print(len(p.program.shows))
#
# print('\n------------------------------\n')
# print('and now meta info')
# for t in p.theaters:
#     print(t.name, t.meta_info)
