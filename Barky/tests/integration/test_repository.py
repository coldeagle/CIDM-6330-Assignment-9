import pytest
import json
from datetime import datetime
from barkylib.adapters.repository import SqlAlchemyRepository
from barkylib.domain.models import Bookmark
from sqlalchemy import create_engine, select, update, delete

pytestmark = pytest.mark.usefixtures("mappers")


def test_add_bookmark(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = SqlAlchemyRepository(session)
    b1 = Bookmark(
        id=1,
        title=f"Google.com",
        url=f"http://google.com",
        notes=f"Source of all truth",
        date_added=datetime(2023, 8, 12),
        date_edited=datetime(2023, 8, 12),
    )
    repo.add_one(b1)
    assert repo.get(b1.id) == b1


def test_add(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = SqlAlchemyRepository(session)

    indexes = ['1', '2', '3']
    # Single create
    repo.add_one(constructBookmark(indexes[0]))
    query = select(Bookmark).where(Bookmark.title.in_(indexes)).order_by(Bookmark.title)
    queried_bmarks = repo.find_all(query)

    assert len(queried_bmarks) == 1

    bmark = repo.get(queried_bmarks[0].id)

    assert bmark is not None
    assert bmark.title == queried_bmarks[0].title

    indexes.remove(indexes[0])
    # Creating multiple bookmarks
    bmarks = create_multiple_bookmarks(repo, indexes)

    assert len(indexes) == len(bmarks)


def test_find(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = SqlAlchemyRepository(session)

    indexes = ['1', '2', '3']
    # Creating the test records
    create_multiple_bookmarks(repo, indexes)

    query = select(Bookmark).where(Bookmark.title.in_(indexes)).order_by(Bookmark.title)

    # Testing single query
    assert repo.find_first(query).title == indexes[0]

    bmarks = repo.find_all(query)

    # Testing multi query
    assert len(bmarks) == len(indexes)


def test_update(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = SqlAlchemyRepository(session)

    indexes = ['1', '2', '3']
    # Creating the test records
    bmarks = create_multiple_bookmarks(repo, indexes)
    # Updating the bookmarks
    for bookmark in bmarks:
        bookmark.notes = 'updated '+bookmark.title
    # Updating the first one
    repo.update(bmarks[0])
    updated_bmark = repo.get(bmarks[0].id)

    # checking that update was applied
    assert bmarks[0].notes == updated_bmark.notes


    # making updates
    repo.update_many(bmarks)

    query = select(Bookmark).where(Bookmark.title.in_(indexes)).order_by(Bookmark.title)
    queried_bmarks = repo.find_all(query)

    # checking to make sure the updates took place
    for i in range(len(bmarks)):
        assert queried_bmarks[i].notes == bmarks[i].notes


def test_delete(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = SqlAlchemyRepository(session)
    indexes = ['1', '2', '3']
    query = select(Bookmark).where(Bookmark.title.in_(indexes)).order_by(Bookmark.title)

    # creating data
    bmarks = create_multiple_bookmarks(repo, indexes)

    # deleting one
    repo.delete_one(bmarks[0])
    queried_bmarks = repo.find_all(query)
    # making sure it was deleted
    assert (len(bmarks) - 1) == len(queried_bmarks)

    # deleting many
    repo.delete_many(queried_bmarks)
    queried_bmarks = repo.find_all(query)
    # making sure all were deleted
    assert len(queried_bmarks) == 0


def create_multiple_bookmarks(repo, indexes) -> list[Bookmark]:
    bmarks = list()
    indexes_as_str = list()
    indexes_as_int = list()

    for index in indexes:
        indexes_as_str.append(str(index))
        indexes_as_int.append(int(index))
        bmarks.append(constructBookmark(int(index)))

    repo.add_many(bmarks)

    query = select(Bookmark).where(Bookmark.title.in_(indexes_as_str)).order_by(Bookmark.title)
    bmarks = repo.find_all(query)

    assert len(bmarks) == len(indexes_as_str)

    return bmarks


def constructBookmark(index) -> Bookmark:
    return Bookmark(
        id=None,
        title=str(index),
        url=f"http://test"+str(index)+".com",
        notes="test "+str(index),
        date_added=datetime(2023, 8, 12),
        date_edited=datetime(2023, 8, 12)
    )
