from collections import OrderedDict

import pytest
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property

from say.constants import OrderingDirection
from say.orm import base
from say.orm import order_by_field
from say.orm import query_builder
from say.orm import session


class Model(base):
    __tablename__ = 'model'
    id = Column(Integer, primary_key=True)
    _password = Column(Integer)
    username = column_property(id + id)

    @hybrid_property
    def hybrid(self):
        return self.id


def test_order_by_field():
    base_query = session.query(Model)

    assert str(order_by_field(Model, base_query, 'id')) == str(
        base_query.order_by(Model.id)
    )
    assert str(order_by_field(Model, base_query, 'id', OrderingDirection.Desc)) == str(
        base_query.order_by(Model.id.desc())
    )

    assert str(order_by_field(Model, base_query, 'username')) == str(
        base_query.order_by(Model.username)
    )

    with pytest.raises(ValueError):
        order_by_field(Model, base_query, '_password')

    with pytest.raises(ValueError):
        order_by_field(Model, base_query, 'hybrid')

    with pytest.raises(ValueError):
        order_by_field(Model, base_query, 'non-existing-column')


def test_query_builder_order_by():
    query = query_builder(
        session,
        Model,
        order_by=OrderedDict(id=OrderingDirection.Asc, username=OrderingDirection.Desc),
    )
    assert str(query) == str(
        session.query(Model).order_by(
            Model.id,
            Model.username.desc(),
        )
    )


def test_query_builder_paginate():
    query = query_builder(session, Model, skip=1, take=5)
    assert str(query) == str(session.query(Model).limit(5).offset(1))


def test_query_builder_filters():
    query = query_builder(session, Model, filters=[Model.id == 1, Model.username == 11])
    assert str(query) == str(
        session.query(Model).filter(Model.id == 1, Model.username == 11)
    )


def test_query_builder_filter_by():
    query = query_builder(session, Model, filter_by=dict(id=1, username=3))
    assert str(query) == str(
        session.query(Model).filter(Model.id == 1, Model.username == 3)
    )


def test_query_builder_filter_callback():
    query = query_builder(
        session,
        Model,
        filter_callbacks=[
            lambda q: q.filter(Model.id == 1),
            lambda q: q.filter(Model.username == 2),
        ],
    )
    assert str(query) == str(
        session.query(Model).filter(Model.id == 1, Model.username == 2)
    )
