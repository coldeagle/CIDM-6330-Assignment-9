import json
import os
import sys
import traceback
from dataclasses import asdict
from pathlib import Path

import pytest
import requests
from barkylib import config
from barkylib.domain.models import Bookmark


def test_api_works(test_client):
    url = config.get_api_url()+'/api/'
    r = test_client.get(f"{url}")

    assert r.status_code == 200
    assert b"Barky API" in r.data


def test_api_add(test_client):
    cleanup(test_client, 1)
    url = config.get_api_url()+'/api/add'
    r = add_bookmark(test_client, 1)

    cleanup(test_client, 1)

    assert r.status_code == 201


def test_get_all(test_client):
    cleanup(test_client, 1)
    cleanup(test_client, 2)

    add_bookmark(test_client, 1)
    add_bookmark(test_client, 2)

    url = config.get_api_url()+'/api/all'

    r = test_client.get(f'{url}')

    data = json.loads(r.data)

    assert len(data) == 2

    cleanup(test_client, 1)
    cleanup(test_client, 2)


def test_edit(test_client):
    index = 1
    cleanup(test_client, index)
    add_bookmark(test_client, index)
    print('bookmark added')
    bmark = get_test_bookmark(test_client, index)
    print('bookmark queried')
    url = config.get_api_url()+'/api/edit/'+str(bmark['id'])
    index = 2
    print('url:'+url)
    r = test_client.post(f"{url}", json=json.loads('{"title":"'+str(index)+'", "url":"http://test'+str(index)+'.com", "notes":"test'+str(index)+'"}'))
    print(r.data)
    print(r.status_code)
    assert r.status_code == 201

    bmark = get_test_bookmark(test_client, index)

    assert str(bmark['title']) == str(index)

    url = config.get_api_url()+'/api/one/'+str(bmark['id'])

    r = test_client.get(f'{url}')
    print(isinstance(bmark, Bookmark))
    print(isinstance(r.data, Bookmark))
    print(r.data)

    assert bmark['title'] == json.loads(r.data)['title']

    cleanup(test_client, index)


def test_get_one(test_client):
    index = 1
    print('cleanup')
    cleanup(test_client, index)
    print('add_bookmark')
    add_bookmark(test_client, index)
    print('get_test_bookmark')
    bmark = get_test_bookmark(test_client, index)
    print('title')
    print(bmark['title'])

    url = config.get_api_url()+'/api/one/'+str(bmark['id'])

    r = test_client.get(f'{url}')
    print(isinstance(bmark, Bookmark))
    print(isinstance(r.data, Bookmark))
    print(r.data)

    assert bmark['title'] == json.loads(r.data)['title']


def add_bookmark(test_client, index):
    url = config.get_api_url()+'/api/add'
    r = test_client.post(f"{url}", json=json.loads('{"title":"'+str(index)+'", "url":"http://test'+str(index)+'.com", "notes":"test'+str(index)+'"}'))
    return r


def get_test_bookmark(test_client, index) -> Bookmark:
    url = config.get_api_url()+'/api/first/title/'+str(index)+'/title'
    print(url)
    r = test_client.get(f'{url}')
    print(r.data)
    if r.data and 'None found' not in str(r.data):
        try:
            return json.loads(r.data)
        except Exception as e:
            print('exception test bookmark')
            traceback.print_exception(*sys.exc_info())
            print(e)
    else:
        return None


def cleanup(test_client, index):
    print('start cleanup')
    bmark = get_test_bookmark(test_client, index)
    try:
        if bmark:
            print(bmark['id'])
            url = config.get_api_url()+'/api/delete/'+str(bmark['id'])
            r = test_client.get(f'{url}')
            print('get after delete')
            print(r.get_data())
    except Exception as e:
        print('exception in cleanup')
        traceback.print_exception(*sys.exc_info())
        print(e)


def delete_db():
    path = Path(__file__).parent.parent.parent

    try:
        os.remove(path / "src/barkylib/bookmarks_test.db")
    except Exception as e:
        print(e)
    try:
        os.remove(path / "src/barkylib/bookmarks.db")
    except Exception as e:
        print(e)

    path = Path(__file__).parent.parent
    try:
        os.remove(path/ "bookmarks.db")
    except Exception as e:
        traceback.print_exception(*sys.exc_info())
        print(e)