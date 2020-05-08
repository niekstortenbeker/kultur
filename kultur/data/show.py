import arrow
import sqlalchemy as sa
from kultur.data.modelbase import SqlAlchemyBase
from sqlalchemy.orm import validates
from sqlalchemy_utils import ArrowType


def default_time(context) -> str:
    return (
        context.get_current_parameters()["date_time"]
        .to("Europe/Berlin")
        .format("HH:mm")
    )


def default_day(context) -> str:
    return (
        context.get_current_parameters()["date_time"]
        .to("Europe/Berlin")
        .format("ddd D.M.", locale="de")
        .upper()
    )


def default_description_start(context) -> str:
    """slice description shorter, try to do so at a logical point in the sentence"""
    desc = context.get_current_parameters()["description"]
    if not desc:
        return desc
    if len(desc) < 300:
        return desc

    desc = desc[0:300]

    last_dot = desc.rfind(".")
    if last_dot > 150:
        return desc[0 : last_dot + 1]

    last_semi_colon = desc.rfind(";")
    if last_semi_colon > 150:
        return desc[0 : last_semi_colon + 1]

    last_comma = desc.rfind(",")
    if last_comma > 150:
        return desc[0 : last_comma + 1]

    return desc[0:250] + " ..."


def default_location_name_url(context) -> str:
    return context.get_current_parameters()["location"].replace(" ", "").lower()


class Show(SqlAlchemyBase):
    __tablename__ = "shows"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    date_time = sa.Column(ArrowType, index=True)
    time = sa.Column(sa.String, default=default_time)
    day = sa.Column(sa.String, default=default_day)
    creation_date = sa.Column(ArrowType, default=arrow.utcnow)

    title = sa.Column(sa.String, index=True)
    description = sa.Column(sa.String, nullable=True)
    description_start = sa.Column(
        sa.String, default=default_description_start, nullable=True
    )
    url_info = sa.Column(sa.String, nullable=True)
    url_tickets = sa.Column(sa.String, nullable=True)

    location = sa.Column(sa.String, index=True)
    location_name_url = sa.Column(sa.String, default=default_location_name_url)
    category = sa.Column(sa.String, index=True)
    dubbed = sa.Column(sa.Boolean, nullable=True, default=False, index=True)
    language_version = sa.Column(sa.String, nullable=True)

    @validates("category")
    def validate_category(self, key, value):
        if value not in ["cinema", "music", "stage"]:
            raise ValueError(
                "only 'cinema', 'stage' and 'music' are accepted categories"
            )
        return value

    @validates("description")
    def validate_description(self, key, value):
        if value:
            return value.strip().replace("\n", "")
        else:
            return ""

    def __repr__(self):
        return f"Show({self.location}, {self.title})"

    def __str__(self):
        return f"Show(id='{self.id}', date_time='{self.date_time}', title='{self.title}', location='{self.location}', category='{self.category}', creation_date='{self.creation_date}', language_version='{self.language_version}', dubbed='{self.dubbed}', url_info='{self.url_info}', url_tickets='{self.url_tickets}', description='{self.description}')"
