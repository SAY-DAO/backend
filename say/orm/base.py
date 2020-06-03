class BaseModel(object):

    @property
    def _column_names(self):
         return [c.name for c in self.__table__.columns]

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwrags)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k not in self._column_names:
                continue

            setattr(self, k, v)
