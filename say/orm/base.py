from collections import OrderedDict

from sqlalchemy.ext.associationproxy import ASSOCIATION_PROXY
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.inspection import inspect
from werkzeug.datastructures import FileStorage

from say.constants import OrderingDirection


class BaseModel(object):
    @property
    def _column_names(self):
        return [c.name for c in self.__table__.columns]

    # This method is depreceted and should be removed
    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k not in self._column_names():
                continue

            if isinstance(v, FileStorage):
                v = v.filepath

            setattr(self, k, v)

    def _update(self, **kwargs):
        for k in columns(
            self,
            synonyms=True,
            hybrids=True,
            proxys=False,
            relationships=False,
            protecteds=False,
        ):
            # for k, v in kwargs.items():
            if k not in kwargs:
                continue

            setattr(self, k, kwargs[k])

    def update_from_schema(self, data):
        self._update(**data.dict(exclude_unset=True))


def columns(
    obj,
    relationships=False,
    synonyms=True,
    composites=False,
    hybrids=True,
    proxys=True,
    protecteds=False,
):
    cls = obj.__class__

    # When obj is model, not instance
    if cls.__class__ == type:
        cls = obj

    mapper = inspect(cls)
    for k, c in mapper.all_orm_descriptors.items():
        if k == '__mapper__' or (
            not protecteds
            and hasattr(c, 'original_property')
            and hasattr(c.original_property, 'info')
            and c.original_property.info.get('protected', False)
        ):
            continue

        if (
            (not hybrids and c.extension_type == HYBRID_PROPERTY)
            or (not relationships and k in mapper.relationships)
            or (not synonyms and k in mapper.synonyms)
            or (not proxys and c.extension_type == ASSOCIATION_PROXY)
            or (not protecteds and k.startswith('_'))
        ):
            continue

        yield k


def order_by_field(
    model,
    query,
    field,
    direction=OrderingDirection.Asc,
):
    if field not in columns(
        model,
        relationships=False,
        synonyms=True,
        composites=False,
        hybrids=False,
        proxys=False,
        protecteds=False,
    ):
        raise ValueError(f'{field} is not a valid field')

    column = getattr(model, field)
    if direction == OrderingDirection.Desc:
        column = column.desc()

    return query.order_by(column)


def query_builder(
    session,
    model,
    filters: list = [],
    filter_callbacks=None,
    filter_by: dict = None,
    skip: int = None,
    take: int = None,
    order_by: OrderedDict = None,
):
    _query = session.query(model)

    # Apply custom filters
    if len(filters) != 0:
        _query = _query.filter(*filters)

    if filter_callbacks:
        for callback in filter_callbacks:
            _query = callback(_query)

    if filter_by:
        _query = _query.filter_by(**filter_by)

    if order_by:
        for field, dir in order_by.items():
            _query = order_by_field(model, _query, field, dir)

    if take:
        _query = _query.limit(take)

    if skip:
        _query = _query.offset(skip)

    return _query
