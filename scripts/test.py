import webscraping
import CreateDatabase
import InputOutput
import time

# webscraping.start_driver()

# try:
#     filmkunst = webscraping.Filmkunst()
#     while True:
#         meta = filmkunst.create_meta_db()
#
# finally:
#     webscraping.close_driver()

#

city46 = webscraping.City46()
program = city46.create_program_db()
# for thing in program:
#     print(thing['info'])

# db_programinfo, db_metainfo, scraping_date = InputOutput.json_to_db()
# db_programinfo = InputOutput.insert_arrow_objects_in_programinfo(db_programinfo)
# for programinfo in db_programinfo:
#     if programinfo['location'] == 'Cinema Ostertor':
#         print(programinfo)
