from asyncio import Future
from pymongo import ASCENDING


class Field:

    def __init__(self, name=None, db_name=None, default=None, required=False, unique=False, sort_order=ASCENDING, before_set=None, after_get=None):
        self.name = name
        self.db_name = db_name
        self.default = default
        self.required = required
        self.unique = unique
        self.sort_order = sort_order
        self.before_set = before_set
        self.after_get = after_get

    def to_mongo(self, value):
        return value

    async def from_mongo(self, value, resolver=None):
        return value

    def is_empty(self, value):
        return value is None

    def validate(self, value):
        return not (self.required and self.is_empty(value))

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if self.name not in instance._values:
            if callable(self.default):
                instance._values[self.name] = self.default()
            else:
                instance._values[self.name] = self.default

        value = instance._values[self.name]

        return value if not self.after_get else self.after_get(value)

    def __set__(self, instance, value):
        instance._values[self.name] = value if not self.before_set else self.before_set(
            value)
        instance._dirty_fields.add(self.name)
