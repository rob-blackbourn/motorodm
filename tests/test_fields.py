import unittest
import motorodm
import re


class TestFields(unittest.TestCase):

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

    def test_Identity(self):

        class DocA(motorodm.Document):
            foo = motorodm.StringField()
            pass

        self.assertEqual(DocA.id.name, 'id', "Should create an 'id' field if not provided")
        self.assertEqual(DocA.id.db_name, '_id', "The 'id' field should have the db_name '_id'")


if __name__ == '__main__':
    unittest.main(exit=False)
