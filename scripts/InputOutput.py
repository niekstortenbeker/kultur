import arrow
import json
from pathlib import Path

basepath = Path(__file__).parent.parent
datapath = basepath / 'data'
scriptpath = basepath / 'scripts'


def remove_arrow_objects_in_program(db_program):
    for theater in db_program:
        for show in db_program[theater]:
            show['date_time'] = show['date_time'].for_json()
    return db_program


def db_to_json(db_programinfo, db_metainfo):
    db_programinfo = remove_arrow_objects_in_program(db_programinfo)
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
    db_programinfo = insert_arrow_objects_in_program(db_programinfo)

    with open(datapath / 'db_metainfo.json', 'r') as f:
        db_metainfo = json.load(f)

    with open(datapath / 'scraping_date.txt', 'r') as f:
        scraping_date = arrow.get(f.read())
    return db_programinfo, db_metainfo, scraping_date


def insert_arrow_objects_in_program(db_program):
    for theater in db_program:
        for show in db_program[theater]:
            show['date_time'] = arrow.get(show['date_time'])
    return db_program


