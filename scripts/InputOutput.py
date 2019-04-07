import arrow
import json
from pathlib import Path

basepath = Path(__file__).parent.parent
datapath = basepath / 'data'
scriptpath = basepath / 'scripts'


def remove_arrow_objects_in_programinfo(db_programinfo):
    for programinfo in db_programinfo:
        programinfo['datetime'] = programinfo['datetime'].for_json()
    return db_programinfo


def db_to_json(db_programinfo, db_metainfo):
    with open(datapath / 'db_programinfo.json', 'w') as f:
        json.dump(db_programinfo, f, indent=2)
        print('\nsaved programinfo to JSON')

    with open(datapath / 'db_metainfo.json', 'w') as f:
        json.dump(db_metainfo, f, indent=2)
        print('\nsaved metainfo to JSON')

    with open(datapath / 'scraping_date.txt', 'w') as f:
        f.write(arrow.now().format())


def json_to_db():
    with open(datapath / 'db_programinfo.json', 'r') as f:
        db_programinfo = json.load(f)

    with open(datapath / 'db_metainfo.json', 'r') as f:
        db_metainfo = json.load(f)

    with open(datapath / 'scraping_date.txt', 'r') as f:
        scraping_date = f.read()
    return db_programinfo, db_metainfo, scraping_date


def insert_arrow_objects_in_programinfo(db_programinfo):
    for programinfo in db_programinfo:
        programinfo['datetime'] = arrow.get(programinfo['datetime'])
    return db_programinfo


