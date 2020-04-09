from pathlib import Path

from data.dbsession import DbSession


def init_database():
    database = Path(__file__).parent.parent / "database" / "kultur.sqlite"
    DbSession.global_init(str(database.resolve()))
