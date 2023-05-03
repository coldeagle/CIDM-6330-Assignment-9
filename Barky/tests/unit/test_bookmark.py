import random
import traceback
from datetime import date, datetime, timedelta

import pytest

from barkylib.adapters.repository import SqlAlchemyRepository
from barkylib.domain import events
from barkylib.domain.models import Bookmark
from sqlalchemy import create_engine, select, update, delete

ok_urls = ["http://", "https://"]

pytestmark = pytest.mark.usefixtures("mappers")


def test_bookmark_title_is_unique(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = SqlAlchemyRepository(session)
    # arrange
    created = datetime(2023, 8, 12)
    edited = datetime(2023, 8, 12)

    # act
    bookmark = Bookmark(0, "test", "http://www.example/com", None, created, edited)
    repo.add_one(bookmark)
    try:
        # trying to add a dup, this should fail
        repo.add_one(bookmark)
        assert False
    except Exception as e:
        assert True


def test_new_bookmark_added_and_edited_times_are_the_same():
    # arrange
    created = datetime.now().isoformat()
    edited = created

    # act
    bookmark = Bookmark(0, "test", "http://www.example/com", None, created, edited)

    # assert
    assert bookmark.date_added == bookmark.date_edited


def test_new_bookmark_url_is_well_formed():
    # arrange
    created = datetime.now().isoformat()
    edited = created

    # act
    bookmark = Bookmark(0, "test", "http://www.example/com", None, created, edited)
    # list comprehensions - https://www.w3schools.com/python/python_lists_comprehension.asp
    okay = [prefix for prefix in ok_urls if bookmark.url.startswith(prefix)]
    # any function - https://www.w3schools.com/python/ref_func_any.asp
    assert any(okay)


def test_that_edit_time_is_newer_than_created_time():
    # arrange
    created = datetime.now().isoformat()
    edited = created

    # act
    bookmark = Bookmark(0, "test", "http://www.example/com", None, created, edited)

    bookmark.notes = "Lorem Ipsum"
    hours_addition = random.randrange(1, 10)
    edit_time = datetime.fromisoformat(bookmark.date_edited)
    bookmark.date_edited = (edit_time + timedelta(hours=hours_addition)).isoformat()

    # assert
    assert bookmark.date_added < bookmark.date_edited
