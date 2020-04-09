import os
from pathlib import Path

from data.dbsession import DbSession


def init_database():
    database = Path(__file__).parent.parent / "database" / "kultur.sqlite"
    if not database.parent.exists():
        os.mkdir(database.parent)
    DbSession.global_init(str(database.resolve()))
