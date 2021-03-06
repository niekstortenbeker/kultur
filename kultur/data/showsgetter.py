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
    When location is '' all locations are searched
    """

    def __init__(
        self,
        start: Arrow,
        stop: Arrow,
        category: str = "all",
        dubbed: bool = False,
        location: str = "",
    ):
        valid_categories = ["all", "cinema", "music", "stage"]
        if type(start) is not Arrow:
            raise TypeError(f"Only Arrow objects accepted")
        if type(stop) is not Arrow:
            raise TypeError(f"Only Arrow objects accepted")
        if type(category) != str:
            raise TypeError("only str accepted")
        if category not in valid_categories:
            raise ValueError(f"'Only categories accepted: {valid_categories}")
        if type(dubbed) is not bool:
            raise TypeError("Only bool accepted")
        if type(location) is not str:
            raise TypeError("only str accepted")
        if not DbSession.factory:
            raise UninitializedDatabaseError("Please call init_database() first")

        self.start: Arrow = start
        self.stop: Arrow = stop
        self.category: str = category
        self.dubbed: bool = dubbed
        self.location = location
        self._session: Session = DbSession.factory()

    def get(self) -> List[Show]:
        """query for shows in the database"""
        shows = self._session.query(Show)
        if self.category != "all":
            shows = shows.filter_by(category=self.category)
        if not self.dubbed:
            shows = shows.filter_by(dubbed=self.dubbed)
        if self.location:
            shows = shows.filter_by(location=self.location)
        shows = (
            shows.filter(Show.date_time >= self.start)
            .filter(Show.date_time < self.stop)
            .order_by(Show.date_time)
        )
        return shows.all()
