from __future__ import annotations

import abc
from abc import ABC

from barkylib import config
from barkylib.adapters import repository
from barkylib.adapters.orm import mapper_registry
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session


class AbstractUnitOfWork(ABC):
    bookmarks: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def collect_new_events(self):
        print('self.bookmarks:')
        print(self.bookmarks)
        print('self.bookmarks.seen:')
        print(self.bookmarks.seen)
        if self.bookmarks.seen:
            for bookmark in self.bookmarks.seen:
                print('bookmark:')
                print(bookmark.events)
                while bookmark.events:
                    yield bookmark.events.pop(0)

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_sqlite_file_url(),
        isolation_level="SERIALIZABLE",
    )
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory
        mapper_registry.metadata.create_all(self.session_factory().get_bind())

    def __enter__(self):
        self.session = self.session_factory()  # type: Session
        self.bookmarks = repository.SqlAlchemyRepository(self.session)

        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
