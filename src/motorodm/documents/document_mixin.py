class EmbeddedDocumentMixin:
    _fields = {}
    _db_name_map = {}
    _dirty_fields = {}

    def __init__(self, **kwargs):
        self._values = {}
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

    def to_dict(self, cls=dict):
        dct = cls()
        for name, field in self._fields.items():
            dct[name] = getattr(self, name, None)
        return dct

    @classmethod
    async def from_mongo(cls, dct, resolver):

        kwargs = {}
        for db_name, value in dct.items():
            field_name = cls._db_name_map[db_name]
            field = cls._fields[field_name]
            value = await field.from_mongo(value, resolver)
            kwargs[field_name] = value

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

    @property
    def _identity(self):
        return getattr(self, self._db_name_map['_id'], None)

    @_identity.setter
    def _identity(self, value):
        return setattr(self, self._db_name_map['_id'], value)

    def __eq__(self, other):
        for name in self._fields.keys():
            if getattr(self, name, None) != getattr(other, name, None):
                return False
        return True

    def __repr__(self):
        name = self.__class__.__name__
        args = ','.join([
            name + '=' + repr(getattr(self, name, None))
            for name, field in self._fields.items()])
        return f"{name}({args})"
        # return str(self.to_dict())


class DocumentMixin(EmbeddedDocumentMixin):

    @classmethod
    def qs(self, db):
        raise Exception('This method is replaced by the metaclass')

    def before_create(self):
        pass

    def before_update(self):
        pass
