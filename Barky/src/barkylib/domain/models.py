from datetime import datetime
import json
from json import JSONEncoder

from sqlalchemy import inspect

from barkylib.domain import events


class Bookmark:
    """
    Pure domain bookmark:
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    notes TEXT,
    date_added TEXT NOT NULL
    date_edited TEXT NOT NULL
    """

    def __init__(
            self,
            id: int = None,
            title: str = None,
            url: str = None,
            notes: str = None,
            date_added: datetime = None,
            date_edited: datetime = None,
    ) -> None:
        self.id = id
        self.title = title
        self.url = url
        self.notes = notes
        self.date_added = date_added
        self.date_edited = date_edited
        self.events = list()  # type: List[events.Event]

    def default(self, o):
        print(self.events)
        return o.__dict__

    def to_json (self):
        return json.dumps(self._asdict(), default=str)

    def _asdict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}
