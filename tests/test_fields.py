import pytest

import motorodm
import re
from tests.utils import run_async


@pytest.mark.unit
def test_StringField(self):

    class MyDocument(motorodm.Document):
        plain = motorodm.StringField()
        upper_case = motorodm.StringField(regex=re.compile('^[A-Z]*$'))

    doc = MyDocument(plain='', upper_case='UPPERCASE')
    self.assertTrue(doc.is_valid, 'Regex patterns should match')

    doc = MyDocument(plain='plain', upper_case='lowercase')
    self.assertFalse(doc.is_valid, 'Regex patterns should not match')

    doc = MyDocument(plain=None, upper_case=None)
    self.assertTrue(doc.is_valid, 'None is ok on string field which are not required')

    doc = MyDocument(plain=1, upper_case=None)
    self.assertFalse(doc.is_valid, "Can't assign a number to a string field")


@pytest.mark.unit
def test_Identity(self):

    class DocA(motorodm.Document):
        foo = motorodm.StringField()
        pass

    # pylint: disable=no-member
    self.assertEqual(DocA.id.name, 'id', "Should create an 'id' field if not provided")
    self.assertEqual(DocA.id.db_name, '_id', "The 'id' field should have the db_name '_id'")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_json_field(self):

    class MyDocument(motorodm.Document):
        field = motorodm.JsonField()

    doc = MyDocument(field={'one': 1, 'two': 2, 'three': [1, 2, 3]})
    dct = doc.to_mongo()

    async def resolve(document_class, value):
        return value

    doc1 = await MyDocument.from_mongo(dct, resolve)
    self.assertEqual(doc, doc1)
