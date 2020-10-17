# noinspection PyUnresolvedReferences
from pathlib import Path

import kultur.data.show  # noqa
import sqlalchemy
import sqlalchemy.orm
from kultur.data import fake_data
from kultur.data.modelbase import SqlAlchemyBase
from kultur.data.show import Show


# custom exception
class UninitializedDatabaseError(Exception):
    """a database connection through DbSession.global_init() is required"""


class DbSession:
    """
    class to initialize a database session

    It will use a postgreSQL database connection for normal data,
    and a local SQLite database for fake data.
    """

    factory = None
    engine = None
    fake_data = None

    @staticmethod
    def global_init(
        user: str, password: str, db: str, host: str = "localhost", port: str = "5432"
    ):
        if DbSession.factory and not DbSession.fake_data:
            return

        DbSession.fake_data = False

        conn_str = f"postgresql://{user}:{password}@{host}:{port}/{db}"
        DbSession._set_engine_and_factory(conn_str)
        print(DbSession.factory)

    @staticmethod
    def global_init_fake_data():
        if DbSession.factory and DbSession.fake_data:
            return

        DbSession.fake_data = True

        db_directory = Path(__file__).parent.absolute() / "kultur_fake.sqlite"
        conn_str = "sqlite:///" + str(db_directory)
        DbSession._set_engine_and_factory(conn_str)

        add_fake_program_to_db()

    @staticmethod
    def close():
        DbSession.factory = None
        DbSession.engine = None
        DbSession.fake_data = None

    @staticmethod
    def _set_engine_and_factory(conn_str: str):
        engine = sqlalchemy.create_engine(conn_str, echo=False)
        DbSession.engine = engine
        DbSession.factory = sqlalchemy.orm.sessionmaker(bind=engine)

        SqlAlchemyBase.metadata.create_all(engine)


def add_fake_program_to_db():
    """populate database with fake data"""
    session = DbSession.factory()
    session.query(Show).delete()
    program = fake_data.complete_program(fake_data.program)
    session.add_all(program)
    session.commit()
