from .meta_document import MetaDocument
from .document_mixin import DocumentMixin


class Document(DocumentMixin, metaclass=MetaDocument):

    __collection__ = None
    _root = True
