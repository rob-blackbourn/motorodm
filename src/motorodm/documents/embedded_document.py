from .meta_document import MetaEmbeddedDocument
from .document_mixin import EmbeddedDocumentMixin


class EmbeddedDocument(EmbeddedDocumentMixin, metaclass=MetaEmbeddedDocument):
    pass
