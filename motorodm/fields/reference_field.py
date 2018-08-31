from .field import Field


class ReferenceField(Field):

    def __init__(self, reference_document_type=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reference_document_type = reference_document_type

    def validate(self, value):
        if value is not None:
            if not isinstance(value, self.reference_document_type):
                return False

        return super().validate(value)

    def to_mongo(self, value):
        return value._identity

    async def from_mongo(self, value, resolver=None):
        return await resolver(self.reference_document_type, value)
