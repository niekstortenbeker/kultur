import webscraping
import CreateDatabase
import InputOutput
import time
from pprint import pprint

# webscraping.start_driver()

# try:
    # filmkunst = webscraping.Filmkunst()
    # filmkunst.update_program()
    # city46 = webscraping.City46()
    # city46.update_program()
    # ostertor = webscraping.CinemaOstertor()
    # ostertor.update_program()
    # ostertor.update_meta_info()
    # print(ostertor.meta_info)
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
# finally:
#     webscraping.close_driver()


p = webscraping.CombinedProgram()
print(f'program / theater: {[t.program for t in p.theaters]}')
print(f'combined program: {p.program}')
p.update_program()

print('---------------------------')
print('programs in the separate theater objects')
for t in p.theaters:
    print(f'{t.name}: {t.program}')

program = [t.program for t in p.theaters]
length = [len(p.shows) for p in program]
print(f'{sum(length)}: length shows in separate theaters')
print(f'combined program: {p.program}')
print(f'{len(p.program.shows)}: lenghts shows in the combined program')


print('\n------------------------------\n')
print('and now meta info')
for t in p.theaters:
    print(t.name, t.meta_info)