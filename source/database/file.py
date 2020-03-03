"""
file handling functions for CombinedProgram (in kultur.py)

Functions
---------
save_to_file(program, metainfo):
    save program and metaInfo to disk
def open_from_file():
    read program, metainfo and scraping_date from disk
"""

import arrow
import json
from pathlib import Path

basepath = Path(__file__).parent.parent.parent
datapath = basepath / "data"
scriptpath = basepath / "scripts"


def save_to_file(program, metainfo):
    """
    save program and metainfo to disk

    writes to datapath/: "program.json", "metainfo.json" and
    "scraping_date.txt".

    Parameters
    ----------
    program: dict
        A dict with theater names as keys, and show lists as values.
        Show list should have show dictionaries containing at least
        a key "date_time" with an arrow object
    metainfo: dict
        A dict with theater names as keys, and show lists as values.
        Show lists contain meta info dicts
    """
    program = _remove_arrow_objects_in_program(program)
    with open(datapath / "program.json", "w") as f:
        json.dump(program, f, indent=2)
        print("\nsaved program to JSON")

    with open(datapath / "metainfo.json", "w") as f:
        json.dump(metainfo, f, indent=2)
        print("\nsaved metainfo to JSON")

    with open(datapath / "scraping_date.txt", "w") as f:
        f.write(arrow.now().format())


def _remove_arrow_objects_in_program(program):
    """
    remove arrow objects from program

    Parameters
    ----------
    program: dict
        A dict with theater names as keys, and show lists as values.
        Show list should have show dictionaries containing at least
        a key "date_time" with an arrow object

    Returns
    -------
    dict
        program with arrow objects ready for json dumping
    """

    for theater in program:
        for show in program[theater]:
            show["date_time"] = show["date_time"].for_json()
    return program


def open_from_file():
    """
    read program, metainfo and scraping_date from disk

    Returns
    -------
    dict
        Program dict with theater names as keys, and show lists as
        values. Show list should have show dictionaries containing at
        least a key "date_time" with an arrow object
    dict
        Metainfo dict with theater names as keys, and show lists as
        values. Show lists contain meta info dicts.
    Arrow object
        scraping date
    """
    with open(datapath / "program.json", "r") as f:
        program = json.load(f)
    program = _insert_arrow_objects_in_program(program)

    with open(datapath / "metainfo.json", "r") as f:
        metainfo = json.load(f)

    with open(datapath / "scraping_date.txt", "r") as f:
        scraping_date = arrow.get(f.read())
    return program, metainfo, scraping_date


def _insert_arrow_objects_in_program(program):
    """
    insert arrow objects in program

    Parameters
    ----------
    program: dict
        Program dict with theater names as keys, and show lists as
        values. Show list should have show dictionaries containing at
        least a key "date_time" with an json representation of an arrow
        object.

    Returns
    -------
    dict
        Program dict with theater names as keys, and show lists as
        values. Show list should have show dictionaries containing at
        least a key "date_time" with an json representation of an arrow
        object.

    """

    for theater in program:
        for show in program[theater]:
            show["date_time"] = arrow.get(show["date_time"])
    return program
