from .field import Field


class ListField(Field):

    def __init__(self, item_field=None, *args, **kwargs):

        if not isinstance(item_field, Field):
            raise ValueError("The item_field for must be a Field")

        super().__init__(*args, **kwargs)

        self.item_field = item_field

    def validate(self, value):
        if value is not None:
            if not isinstance(value, list):
                return False

            for item in value:
                if not self.item_field.validate(item):
                    return False

        return super().validate(value)

    def is_empty(self, value):
        return value is None or len(value) == 0

    def to_mongo(self, value):
        return None if value is None else [self.item_field.to_mongo(item) for item in value]

    async def from_mongo(self, value, resolver=None):
        if value is None:
            return []
        return [await self.item_field.from_mongo(item, resolver) for item in value]
