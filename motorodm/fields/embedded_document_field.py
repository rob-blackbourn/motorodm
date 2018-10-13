from .field import Field
from ..utils.types import is_callable


class EmbeddedDocumentField(Field):

    def __init__(self, embedded_document_type=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._embedded_document_type = embedded_document_type

    @property
    def embedded_document_type(self):
        if is_callable(self._embedded_document_type):
            self._embedded_document_type = self._embedded_document_type()
        return self._embedded_document_type

    def validate(self, value):
        if value is not None:
            if not isinstance(value, self.embedded_document_type):
                return False

        return super().validate(value)

    def to_mongo(self, value):
        return self.embedded_document_type.to_mongo(value)

    async def from_mongo(self, value, resolver=None):
        return await self.embedded_document_type.from_mongo(value, resolver)
