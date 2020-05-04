# noinspection PyUnresolvedReferences
import kultur.data.show  # noqa
import sqlalchemy
import sqlalchemy.orm
from kultur.data.modelbase import SqlAlchemyBase


# custom exception
class UninitializedDatabaseError(Exception):
    """a database connection through DbSession.global_init() is required"""


class DbSession:
    factory = None
    engine = None

    @staticmethod
    def global_init(db_file: str):
        if DbSession.factory:
            return

        if not db_file or not db_file.strip() or not isinstance(db_file, str):
            raise ValueError("You must specify a data file as str")

        conn_str = "sqlite:///" + db_file
        # print("Connecting to DB at: {}".format(conn_str))

        engine = sqlalchemy.create_engine(conn_str, echo=True)
        DbSession.engine = engine
        DbSession.factory = sqlalchemy.orm.sessionmaker(bind=engine)

        SqlAlchemyBase.metadata.create_all(engine)

    @staticmethod
    def close():
        DbSession.factory = None
        DbSession.engine = None
