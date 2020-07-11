import os
import tempfile

import pytest
from sqlalchemy import create_engine

from say.api import api
from say.orm import metadata


# def test_empty_db(client):
#     rv = client.get('/')
#     assert b'No entries here so far' in rv.data
#
#
# def test_panel_login(client):
#     rv = login(client, 'babak', '123456')
#     print(rv.get_json())
#     assert 'success' in rv.get_json()
#
#
# def login(client, username, password):
#     return client.post('/api/v2/panel/auth/login', json={'username': username, 'password': password},
#                        follow_redirects=True)
#
#
# def logout(client):
#     return client.get('/api/v2/panel/auth/logout/userid=<user_id>', follow_redirects=True)
