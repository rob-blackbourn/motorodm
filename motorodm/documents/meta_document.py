from ..fields.field import Field
from ..fields import ObjectIdField
from ..query_sets.query_set import QuerySet


class MetaEmbeddedDocument(type):

    def __new__(cls, name, bases, dct):

        dct['_fields'] = {}
        dct['_db_name_map'] = {}
        dct['_indices'] = []

        for base in bases:
            for field_name, field in filter(lambda x: isinstance(x[1], Field), base.__dict__.items()):
                cls.add_field(dct, field_name, field)

        for field_name, field in filter(lambda x: isinstance(x[1], Field), dct.items()):
            field.name = field_name
            cls.add_field(dct, field_name, field)

        dct['_values'] = {}
        dct['_dirty_fields'] = set()

        return super().__new__(cls, name, bases, dct)

    @classmethod
    def add_field(cls, dct, field_name, field):
        if field_name in dct['_fields']:
            raise KeyError(f"Field '{field_name}' already exists")
        if not field.db_name:
            field.db_name = field_name
        if field.db_name in dct['_db_name_map']:
            raise KeyError(f"Field '{field_name}' already exists")
        field.name = field_name
        dct['_fields'][field_name] = field
        dct['_db_name_map'][field.db_name] = field_name
        if field.unique:
            dct['_indices'].append(field_name)


class MetaDocument(MetaEmbeddedDocument):

    def __new__(cls, name, bases, dct):

        if '_root' in dct and dct['_root']:
            return super().__new__(cls, name, bases, dct)

        if dct.get('__collection__', None) is None:
            dct['__collection__'] = name

        klass = super().__new__(cls, name, bases, dct)

        if '_id' not in klass._db_name_map:
            if 'id' in klass.__dict__:
                raise Exception('Unable to set id field - already exists')
            field = ObjectIdField(name='id', db_name='_id')
            klass.id = field
            klass._fields[field.name] = field
            klass._db_name_map[field.db_name] = field.name

        klass.qs = QuerySet()

        return klass
