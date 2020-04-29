from typing import List

from arrow.arrow import Arrow
from kultur.data.dbsession import DbSession, UninitializedDatabaseError
from kultur.data.show import Show
from sqlalchemy.orm import Session


class ShowsGetter:
    """
    Class to query shows in the database.

    Requires initialized DbSession.
    Category can be "all", "cinema", "music" or "stage".
    """

    def __init__(
        self, start: Arrow, stop: Arrow, category: str = "all", dubbed: bool = False
    ):
        if type(start) is not Arrow:
            raise TypeError("only Arrow accepted")
        if type(stop) is not Arrow:
            raise TypeError("only Arrow accepted")
        if category not in ["all", "cinema", "music", "stage"]:
            raise ValueError("not a valid category")
        if type(dubbed) is not bool:
            raise TypeError("only bool accepted")
        if not DbSession.factory:
            raise UninitializedDatabaseError("Please call init_database() first")

        self.start: Arrow = start
        self.stop: Arrow = stop
        self.category: str = category
        self.dubbed: bool = dubbed
        self._session: Session = DbSession.factory()

    def get(self) -> List[Show]:
        """query for shows in the database"""
        shows = self._session.query(Show)
        if self.category != "all":
            shows = shows.filter_by(category=self.category)
        if not self.dubbed:
            shows = shows.filter_by(dubbed=self.dubbed)
        return (
            shows.filter(Show.date_time.between(self.start, self.stop))
            .order_by(Show.date_time)
            .all()
        )
