from sqlalchemy import orm


def lenient_constructor(self, **kwargs):
    cls_ = type(self)
    for k in kwargs:
        if hasattr(cls_, k):
            setattr(self, k, kwargs[k])


registry = orm.registry(constructor=lenient_constructor)


class BaseModel(orm.DeclarativeBase):
    registry = registry
