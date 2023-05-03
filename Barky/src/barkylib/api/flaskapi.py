import json
import sys
from datetime import datetime

from barkylib import bootstrap, views
from barkylib.services import unit_of_work, handlers
from barkylib.adapters.repository import *
from barkylib.domain import commands

# init from dotenv file
from dotenv import load_dotenv
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from .baseapi import AbstractBookMarkAPI


load_dotenv()

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookmarks.db'
# db = SQLAlchemy(app)
bus = bootstrap.bootstrap()


class FlaskBookmarkAPI(AbstractBookMarkAPI):
    """
    Flask
    """

    def __init__(self) -> None:
        super().__init__()

    # @app.route("/")
    def index(self):
        return f"Barky API"

    # @app.route("/api/one/<id>")
    def one(self, id):
        try:

            bookmarks = views.get_bookmarks(bus.uow, id)
            if bookmarks is None:
                return 'None found', 204
            else:
                return json.dumps(bookmarks[0]), 200

        except Exception as e:
            print('one except')
            traceback.print_exception(*sys.exc_info())
            print(e)
            return str(e), 400

    # @app.route("/api/all")
    def all(self):
        return self.many(filter=None, value=None, sort=None)

    # @app.route("/api/first/<property>/<value>/<sort>")
    def first(self, filter, value, sort):
        bookmarks = self.many(filter, value, sort)
        if bookmarks:
            return bookmarks[0]
        else:
            return bookmarks

    def many(self, filter, value, sort):
        try:
            cmd = commands.ListBookmarksCommand(
                filter=filter, value=value, order_by=sort
            )

            bus.handle(cmd)
            bookmarks = cmd.bookmarks

            if bookmarks is None or not bookmarks:
                return 'None found', 204
            else:
                return bookmarks
        except Exception as e:
            print('many except')
            print(e)
            return str(e), 400

    def add(self, bookmark):
        try:
            cmd = commands.AddBookmarkCommand(
                id=bookmark.id,
                title=bookmark.title,
                url=bookmark.url,
                notes=bookmark.notes,
                date_added=bookmark.date_added,
                date_edited=bookmark.date_edited
            )
            bus.handle(cmd)

            return 'OK', 201
        except Exception as e:
            print('add except')
            traceback.print_exception(*sys.exc_info())
            return str(e), 400

    def add_bookmark(self):
        return self.add(bookmark=self.get_bookmark_from_json(request.get_json(force=True)))

    def delete(self, bookmark):
        print('delete')
        try:
            id = None
            try:
                id = bookmark.id
            except Exception as e:
                id = bookmark['id']

            cmd = commands.DeleteBookmarkCommand(
                id=id
            )
            print('cmd')
            bus.handle(cmd)

            return 'OK', 201

        except Exception as e:
            print('delete except')
            traceback.print_exception(*sys.exc_info())
            print(e)
            return str(e), 400

    def delete_bookmark(self, id):
        try:

            self.delete(dict(id=id))
            return 'Ok', 200
        except Exception as e:
            return str(e), 400

    def update_bookmark(self, id):
        print('update_bookmark')
        print(request.get_json(force=True))
        bookmark = self.get_bookmark_from_json(request.get_json(force=True))
        bookmark.id = id
        print('is instance of bookmark?')
        print(isinstance(bookmark, Bookmark))
        print(bookmark.id)
        return self.update(bookmark=bookmark)

    def update(self, bookmark):
        print('update')
        print(bookmark.id)
        try:
            cmd = commands.EditBookmarkCommand(
                id=bookmark.id,
                title=bookmark.title,
                notes=bookmark.notes,
                url=bookmark.url,
                date_edited=bookmark.date_edited,
                date_added=bookmark.date_added,
            )

            bus.handle(cmd)

            return 'OK', 201

        except Exception as e:
            print('update except')
            traceback.print_exception(*sys.exc_info())
            print(e)
            return str(e), 400

    def get_bookmark_from_json(self, req_json) -> Bookmark:
        print(req_json.get('id'))
        return Bookmark(
            id=req_json.get('id'),
            title=req_json.get('title'),
            url=req_json.get('url'),
            notes=req_json.get('notes'),
            date_added=req_json.get('date_added'),
            date_edited=datetime.now()
        )


fb = FlaskBookmarkAPI()
bp = Blueprint("flask_bookmark_api", __name__, url_prefix="/api")

# @app.route('/')
bp.add_url_rule("/", "index", fb.index, ["GET"])

# @app.route('/api/one/<id>')
bp.add_url_rule("/one/<id>", "one", fb.one, ["GET"])

# @app.route('/api/all')
bp.add_url_rule("/all", "all", fb.all, ["GET"])

# @app.route('/api/add')
bp.add_url_rule("/add", "add", fb.add_bookmark, methods=["POST"])

# @app.route('/api/edit/<id>')
bp.add_url_rule("/edit/<id>", "edit", fb.update_bookmark, methods=["POST"])

# @app.route('/api/delete/<id>')
bp.add_url_rule("/delete/<id>", "delete", fb.delete_bookmark, methods=["GET"])

# @app.route("/api/first/<filter>/<value>/<sort>")
bp.add_url_rule('/first/<filter>/<value>/<sort>', "first", fb.first, methods=["GET"])