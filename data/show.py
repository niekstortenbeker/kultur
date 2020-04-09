import arrow
import sqlalchemy as sa
from data.modelbase import SqlAlchemyBase
from sqlalchemy_utils import ArrowType


class Show(SqlAlchemyBase):
    __tablename__ = "shows"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    date_time = sa.Column(ArrowType, index=True)
    title = sa.Column(sa.String, index=True)
    location = sa.Column(sa.String, index=True)
    # category = 'cinema', 'music' or 'stage'
    category = sa.Column(sa.String, index=True)
    creation_date = sa.Column(ArrowType, default=arrow.utcnow)
    description = sa.Column(sa.String, nullable=True)
    language_version = sa.Column(sa.String, nullable=True)
    dubbed = sa.Column(sa.Boolean, nullable=True, default=False)
    url_info = sa.Column(sa.String, nullable=True)
    url_tickets = sa.Column(sa.String, nullable=True)

    def __repr__(self):
        return f"Show({self.location}, {self.title})"

    def __str__(self):
        return f"Show(id='{self.id}', date_time='{self.date_time}', title='{self.title}', location='{self.location}', category='{self.category}', creation_date='{self.creation_date}', language_version='{self.language_version}', dubbed='{self.dubbed}', url_info='{self.url_info}', url_tickets='{self.url_tickets}', description='{self.description}')"
