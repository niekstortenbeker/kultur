# noinspection PyUnresolvedReferences
import data.show  # noqa: F401
import sqlalchemy
import sqlalchemy.orm
from data.modelbase import SqlAlchemyBase


class DbSession:
    factory = None
    engine = None

    @staticmethod
    def global_init(db_file: str):
        if DbSession.factory:
            return

        if not db_file or not db_file.strip():
            raise Exception("You must specify a data file")

        conn_str = "sqlite:///" + db_file
        print("Connecting to DB at: {}".format(conn_str))

        engine = sqlalchemy.create_engine(conn_str, echo=True)
        DbSession.engine = engine
        DbSession.factory = sqlalchemy.orm.sessionmaker(bind=engine)

        SqlAlchemyBase.metadata.create_all(engine)

    @staticmethod
    def close():
        DbSession.factory = None
        DbSession.engine = None
