from .meta_document import MetaDocument


class Document(metaclass=MetaDocument):
    _root = True
    _fields = {}
    _db_name_map = {}
    _dirty_fields = {}

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            if name in self._fields:
                setattr(self, name, value)
        self._make_clean()

    def to_mongo(self):
        data = {}
        for field in self._fields.values():
            value = field.to_mongo(
                getattr(self, field.name, None))
            if value is not None:
                data[field.db_name] = value
        return data

    @classmethod
    def from_mongo(cls, dct):

        kwargs = {}
        for db_name, value in dct.items():
            field_name = cls._db_name_map[db_name]
            field = cls._fields[field_name]
            kwargs[field_name] = field.from_mongo(value)

        return cls(**kwargs)

    @property
    def is_valid(self):
        for field in self._fields.values():
            if not field.validate(getattr(self, field.name, None)):
                return False
        return True

    @property
    def is_dirty(self):
        return len(self._dirty_fields) > 0

    def _make_clean(self):
        self._dirty_fields = set()

    def __eq__(self, other):
        for name in self._fields.keys():
            if getattr(self, name, None) != getattr(other, name, None):
                return False
        return True

    @classmethod
    def qs(self, db):
        raise Exception('This method is replaced by the metaclass')
