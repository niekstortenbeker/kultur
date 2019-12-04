import arrow
import json
from pathlib import Path

basepath = Path(__file__).parent.parent
datapath = basepath / 'data'
scriptpath = basepath / 'scripts'


def save_to_file(program, metainfo):
    program = remove_arrow_objects_in_program(program)
    with open(datapath / 'program.json', 'w') as f:
        json.dump(program, f, indent=2)
        print('\nsaved program to JSON')

    with open(datapath / 'metainfo.json', 'w') as f:
        json.dump(metainfo, f, indent=2)
        print('\nsaved metainfo to JSON')

    with open(datapath / 'scraping_date.txt', 'w') as f:
        f.write(arrow.now().format())


def remove_arrow_objects_in_program(program):
    for theater in program:
        for show in program[theater]:
            show['date_time'] = show['date_time'].for_json()
    return program


def open_from_file():
    with open(datapath / 'program.json', 'r') as f:
        program = json.load(f)
    program = insert_arrow_objects_in_program(program)

    with open(datapath / 'metainfo.json', 'r') as f:
        metainfo = json.load(f)

    with open(datapath / 'scraping_date.txt', 'r') as f:
        scraping_date = arrow.get(f.read())
    return program, metainfo, scraping_date


def insert_arrow_objects_in_program(program):
    for theater in program:
        for show in program[theater]:
            show['date_time'] = arrow.get(show['date_time'])
    return program


