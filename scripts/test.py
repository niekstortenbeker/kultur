import webscraping
import CreateDatabase
import InputOutput
import time
from pprint import pprint

webscraping.start_driver()

# try:
#     filmkunst = webscraping.Filmkunst()
#     while True:
#         meta = filmkunst.create_meta_db()
#
# finally:
#     webscraping.close_driver()

#

ostertor = webscraping.CinemaOstertor()
program = ostertor.create_program_db()
# meta = ostertor.create_meta_db()
pprint(program)

webscraping.close_driver()


# db_programinfo, db_metainfo, scraping_date = InputOutput.json_to_db()
# db_programinfo = InputOutput.insert_arrow_objects_in_programinfo(db_programinfo)
# for programinfo in db_programinfo:
#     if programinfo['location'] == 'Cinema Ostertor':
#         print(programinfo)
