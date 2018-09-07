from bson import ObjectId
from .field import Field


class ObjectIdField(Field):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_mongo(self, value):
        return ObjectId(value) if value else None

    async def from_mongo(self, value, resolver=None):
        return str(value) if value else None
