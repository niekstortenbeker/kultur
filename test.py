import CreateDatabase
import webscraping
import output


db_programinfo, db_metainfo = output.json_to_db()
db_programinfo = output.insert_arrow_objects_in_programinfo(db_programinfo)
output.quality_control_dbs(db_programinfo, db_metainfo)