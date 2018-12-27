import webscraping
import CreateDatabase


# webscraping.start_driver()

# try:
#     filmkunst = webscraping.Filmkunst()
#     while True:
#         meta = filmkunst.create_meta_db()
#
# finally:
#     webscraping.close_driver()

#

kukoon = webscraping.Kukoon()
program = kukoon.create_program_db()
for thing in program:
    print(thing['info'])

