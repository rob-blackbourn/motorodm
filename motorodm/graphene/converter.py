from graphene import (ID, Boolean, Dynamic, Field, Float, Int, List,
                      NonNull, String, is_node)
from graphene.types.json import JSONString

import motorodm

from motorodm.graphene.fields import MotorOdmConnectionField

from functools import singledispatch


@singledispatch
def convert_motorodm_field(field, registry=None):
    raise Exception(
        "Don't know how to convert the MotorOdm field %s (%s)" %
        (field, field.__class__))


@convert_motorodm_field.register(motorodm.fields.StringField)
def convert_field_to_string(field, registry=None):
    return String(description=field.db_field, required=field.required)


@convert_motorodm_field.register(motorodm.fields.ObjectIdField)
def convert_field_to_id(field, registry=None):
    return ID(description=field.db_field, required=field.required)


@convert_motorodm_field.register(motorodm.fields.IntField)
# @convert_motorodm_field.register(motorodm.fields.LongField)
def convert_field_to_int(field, registry=None):
    return Int(description=field.db_field, required=field.required)


@convert_motorodm_field.register(motorodm.fields.BooleanField)
def convert_field_to_boolean(field, registry=None):
    return NonNull(Boolean, description=field.db_field)


@convert_motorodm_field.register(motorodm.fields.DecimalField)
@convert_motorodm_field.register(motorodm.fields.FloatField)
def convert_field_to_float(field, registry=None):
    return Float(description=field.db_field, required=field.required)


# @convert_motorodm_field.register(motorodm.fields.DictField)
# @convert_motorodm_field.register(motorodm.fields.MapField)
# def convert_dict_to_jsonstring(field, registry=None):
#     return JSONString(description=field.db_field, required=field.required)


@convert_motorodm_field.register(motorodm.fields.DateTimeField)
def convert_date_to_string(field, registry=None):
    return String(description=field.db_field, required=field.required)


@convert_motorodm_field.register(motorodm.fields.ListField)
# @convert_motorodm_field.register(motorodm.fields.EmbeddedDocumentListField)
def convert_field_to_list(field, registry=None):
    # pylint: disable=assignment-from-no-return
    base_type = convert_motorodm_field(field.field, registry=registry)
    if isinstance(base_type, (Dynamic)):
        base_type = base_type.get_type()
        if base_type is None:
            return
        base_type = base_type._type

    if is_node(base_type):
        return MotorOdmConnectionField(base_type)

    # Non-relationship field
    relations = (motorodm.fields.ReferenceField,
                 motorodm.fields.EmbeddedDocumentField)
    if not isinstance(base_type, (List, NonNull)) \
            and not isinstance(field.field, relations):
        base_type = type(base_type)

    return List(base_type, description=field.db_field, required=field.required)


@convert_motorodm_field.register(motorodm.fields.EmbeddedDocumentField)
@convert_motorodm_field.register(motorodm.fields.ReferenceField)
def convert_field_to_dynamic(field, registry=None):
    model = field.document_type

    def dynamic_type():
        _type = registry.get_type_for_model(model)
        if not _type:
            return None
        return Field(_type)

    return Dynamic(dynamic_type)
