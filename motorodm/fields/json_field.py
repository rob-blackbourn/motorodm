from bson.json_util import loads, dumps
from .field import Field


class JsonField(Field):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_mongo(self, value):
        return dumps(value) if value else None

    async def from_mongo(self, value, resolver=None):
        return loads(value) if value else None
