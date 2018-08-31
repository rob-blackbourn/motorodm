from unittest import TestCase
from motorodm import Document
from motorodm import StringField, ListField


class TestDocument(TestCase):

    def test_smoke(self):

        class User(Document):
            first_name = StringField(db_name='firstName')
            last_name = StringField(db_name='lastName')

        class PermissionedUser(User):
            roles = ListField(item_field=StringField())

        self.assertEqual(PermissionedUser.first_name.name, "first_name")
        self.assertEqual(PermissionedUser.first_name.db_name, "firstName")
        self.assertEqual(PermissionedUser.last_name.name, "last_name")
        self.assertEqual(PermissionedUser.last_name.db_name, "lastName")
        self.assertEqual(PermissionedUser.roles.name, "roles")
        self.assertEqual(PermissionedUser.roles.db_name, "roles")

        user = PermissionedUser(
            first_name='Rob',
            last_name='Blackbourn',
            roles=['a', 'b', 'c'])

        self.assertFalse(user.is_dirty)
        self.assertEqual(user.first_name, 'Rob')
        self.assertEqual(user.last_name, 'Blackbourn')
        self.assertEqual(user.roles, ['a', 'b', 'c'])
        self.assertTrue(user.is_valid)

        user.first_name = 'Thomas'
        self.assertEqual(user.first_name, 'Thomas')
        self.assertTrue(user.is_dirty)
        user._make_clean()
        self.assertFalse(user.is_dirty)

        user2 = PermissionedUser.from_mongo(user.to_mongo())
        self.assertFalse(user2.is_dirty)
        self.assertEqual(user2, user)
        self.assertTrue(user2.is_valid)
