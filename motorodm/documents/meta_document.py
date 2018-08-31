from ..fields.field import Field
from ..fields import ObjectIdField
from ..query_sets.query_set import QuerySet


class MetaDocument(type):

    def __new__(cls, name, bases, dct):

        if '_root' in dct and dct['_root']:
            return super().__new__(cls, name, bases, dct)

        dct['_fields'] = {}
        dct['_db_name_map'] = {}
        dct['_indices'] = []

        for base in bases:
            for field_name, field in filter(lambda x: isinstance(x[1], Field), base.__dict__.items()):
                MetaDocument.add_field(dct, field_name, field)

        for field_name, field in filter(lambda x: isinstance(x[1], Field), dct.items()):
            field.name = field_name
            MetaDocument.add_field(dct, field_name, field)

        if '_id' not in dct['_db_name_map']:
            cls.add_field(dct, '_id', ObjectIdField())

        dct['_values'] = {}
        dct['_dirty_fields'] = set()
        dct['qs'] = QuerySet()

        if '__collection__' not in dct:
            dct['__collection__'] = name

        klass = super().__new__(cls, name, bases, dct)

        return klass

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
