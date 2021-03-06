import pytest

import motorodm
import re


@pytest.mark.unit
def test_StringField():
    class MyDocument(motorodm.Document):
        plain = motorodm.StringField()
        upper_case = motorodm.StringField(regex=re.compile('^[A-Z]*$'))

    doc = MyDocument(plain='', upper_case='UPPERCASE')
    assert doc.is_valid, 'Regex patterns should match'

    doc = MyDocument(plain='plain', upper_case='lowercase')
    assert not doc.is_valid, 'Regex patterns should not match'

    doc = MyDocument(plain=None, upper_case=None)
    assert doc.is_valid, 'None is ok on string field which are not required'

    doc = MyDocument(plain=1, upper_case=None)
    assert not doc.is_valid, "Can't assign a number to a string field"


@pytest.mark.unit
def test_Identity():
    class DocA(motorodm.Document):
        foo = motorodm.StringField()
        pass

    # pylint: disable=no-member
    assert DocA.id.name == 'id', "Should create an 'id' field if not provided"
    assert DocA.id.db_name == '_id', "The 'id' field should have the db_name '_id'"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_json_field():
    class MyDocument(motorodm.Document):
        field = motorodm.JsonField()

    doc = MyDocument(field={'one': 1, 'two': 2, 'three': [1, 2, 3]})
    dct = doc.to_mongo()

    async def resolve(document_class, value):
        return value

    doc1 = await MyDocument.from_mongo(dct, resolve)
    assert doc == doc1


def test_reference_field():
    class Address(motorodm.Document):
        city = motorodm.StringField()

    class Person(motorodm.Document):
        name = motorodm.StringField()
        address = motorodm.ReferenceField(reference_document_type=Address)

    address = Address(city='London')
    person = Person(name='Rob', address=address)

    assert person.address.city == 'London'
    assert person.is_valid


def test_recursive_reference_field():
    class Person(motorodm.Document):
        name = motorodm.StringField(required=True, unique=True)
        parent = motorodm.ReferenceField(reference_document_type=lambda: Person)

    grandparent = Person(name='grandparent')
    parent = Person(name='parent', parent=grandparent)
    child = Person(name='child', parent=parent)

    assert child.parent.parent.name == 'grandparent'
    assert child.is_valid
