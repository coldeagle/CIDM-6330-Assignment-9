"""
This module utilizes the command pattern - https://en.wikipedia.org/wiki/Command_pattern - to
specify and implement the business logic layer
"""
import sys
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests

# from database import DatabaseManager

# module scope
# db = DatabaseManager("bookmarks.db")


class Command(ABC):
    pass


@dataclass
class AddBookmarkCommand(Command):
    """
    This command is a dataclass that encapsulates a bookmark
    This uses type hints: https://docs.python.org/3/library/typing.html
    """

    id: int
    title: str
    url: str
    # data["date_added"] = datetime.utcnow().isoformat()
    date_added: str
    date_edited: str
    notes: Optional[str] = None


@dataclass
class ListBookmarksCommand(Command):
    filter: Optional[str] = None
    value: Optional[object] = None
    order_by: Optional[str] = None
    order: Optional[str] = None
    query: Optional[object] = None
    bookmarks: Optional[list[object]] = None


@dataclass
class DeleteBookmarkCommand(Command):
    id: int


@dataclass
class EditBookmarkCommand(Command):
    id: int
    title: Optional[str]
    url: Optional[str]
    date_added: Optional[str]
    date_edited: Optional[str]
    notes: Optional[str] = None
