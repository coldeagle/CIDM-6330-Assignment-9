from barkylib.services import unit_of_work
from barkylib.domain import models
from sqlalchemy.sql import text


def get_bookmarks(uow: unit_of_work.SqlAlchemyUnitOfWork, bookmark_id: int):

    with uow:
        if bookmark_id is not None:
            results = uow.session.execute(text('SELECT id, title, url, notes, date_edited, date_added FROM bookmarks_view WHERE id = :bookmark_id'), dict(bookmark_id=bookmark_id))
        else:
            results = uow.session.execute(text('SELECT id, title, url, notes, date_edited, date_added FROM bookmarks_view'))

    return_list = list()
    print('printing results')
    for r in results:
        return_list.append(dict(id=r[0], title=r[1], url=r[2], notes=r[3], date_edited=r[4], date_added=r[5]))

    print(return_list)

    return return_list
