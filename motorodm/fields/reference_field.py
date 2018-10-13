from .field import Field
from ..utils.types import is_callable


class ReferenceField(Field):

    def __init__(self, reference_document_type=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reference_document_type = reference_document_type

    @property
    def reference_document_type(self):
        if is_callable(self._reference_document_type):
            self._reference_document_type = self._reference_document_type()
        return self._reference_document_type

    def validate(self, value):
        if value is not None:
            if not isinstance(value, self.reference_document_type):
                return False

        return super().validate(value)

    def to_mongo(self, value):
        return value._identity

    async def from_mongo(self, value, resolver=None):
        value = await resolver(self.reference_document_type, value)
        return value
