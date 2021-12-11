"""
Modified version of the original Flask pluging.
https://github.com/kvesteri/sqlalchemy-continuum/blob/52594a3019a4a38c911389c258a88b4a3e73f20a/sqlalchemy_continuum/plugins/flask.py


FlaskPlugin offers way of integrating Flask framework with
SQLAlchemy-Continuum. Flask-Plugin adds two columns for Transaction model,
namely `user_id` and `remote_addr`.
These columns are automatically populated when transaction object is created.
The `remote_addr` column is populated with the value of the remote address that
made current request. The `user_id` column is populated with the id of the
current_user object.
::
    from sqlalchemy_continuum.plugins import FlaskPlugin
    from sqlalchemy_continuum import make_versioned
    make_versioned(plugins=[FlaskPlugin()])
"""
from __future__ import absolute_import


flask = None
try:
    import flask
    from flask import request
    from flask.globals import _app_ctx_stack
    from flask.globals import _request_ctx_stack
except ImportError:
    pass

from sqlalchemy_continuum.plugins.base import Plugin
from sqlalchemy_utils import ImproperlyConfigured


def fetch_current_user_id():
    # Return None if we are outside of request context.
    if _app_ctx_stack.top is None or _request_ctx_stack.top is None:
        return
    try:
        return request.user.id
    except AttributeError:
        return


def fetch_remote_addr():
    # Return None if we are outside of request context.
    if _app_ctx_stack.top is None or _request_ctx_stack.top is None:
        return

    from say.api.ext.remote_address import get_remote_address

    return get_remote_address()


class FlaskPlugin(Plugin):
    def __init__(self, current_user_id_factory=None, remote_addr_factory=None):
        self.current_user_id_factory = (
            fetch_current_user_id
            if current_user_id_factory is None
            else current_user_id_factory
        )
        self.remote_addr_factory = (
            fetch_remote_addr if remote_addr_factory is None else remote_addr_factory
        )

        if not flask:
            raise ImproperlyConfigured(
                'Flask is required with FlaskPlugin. Please install Flask by'
                ' running pip install Flask'
            )

    def transaction_args(self, uow, session):
        return {
            'user_id': self.current_user_id_factory(),
            'remote_addr': self.remote_addr_factory(),
        }


flask_versioning_plugin = FlaskPlugin(
    current_user_id_factory=fetch_current_user_id(),
    remote_addr_factory=fetch_remote_addr(),
)
