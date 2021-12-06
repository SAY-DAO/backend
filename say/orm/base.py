from sqlalchemy.ext.associationproxy import ASSOCIATION_PROXY
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.inspection import inspect
from werkzeug.datastructures import FileStorage


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
        for k, c in columns(
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
        ):
            continue

        yield k, getattr(cls, k)
