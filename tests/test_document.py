import unittest
from asyncio import Future

from motorodm import Document, EmbeddedDocument
from motorodm import StringField, ListField, ReferenceField, EmbeddedDocumentField
from bson import ObjectId

from tests.utils import run_async


class TestDocument(unittest.TestCase):

    @run_async
    async def test_smoke(self):

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

        user2 = await PermissionedUser.from_mongo(user.to_mongo(), None)
        self.assertFalse(user2.is_dirty)
        self.assertEqual(user2, user)
        self.assertTrue(user2.is_valid)

    def test_identity(self):

        class User(Document):
            name = StringField()

        id = str(ObjectId())
        user = User(id=id, name='Fred')
        self.assertTrue(user.is_valid)
        self.assertEqual(id, user._identity)

        id2 = str(ObjectId())
        user._identity = id2
        self.assertEqual(id2, user._identity)

    @run_async
    async def test_reference_field(self):

        class User(Document):
            name = StringField()

        class Post(Document):
            user = ReferenceField(User)
            title = StringField()
            body = StringField()

        user = User(id=str(ObjectId()), name='Rob')
        post = Post(id=str(ObjectId()), user=user,
                    title='My Post', body='Words of wisdom')

        self.assertTrue(post.is_valid)
        dct = post.to_mongo()
        self.assertIn('user', dct)

        async def resolve(document_class, value):
            return user

        post2 = await Post.from_mongo(dct, resolve)
        self.assertEqual(post, post2)

    @run_async
    async def test_embedded_document(self):

        class Address(EmbeddedDocument):
            street = StringField()
            town = StringField()

        class User(Document):
            name = StringField()
            address = EmbeddedDocumentField(Address)

        user = User(name='Fred', address=Address(
            street='1 Main Street', town='Atlantis'))

        self.assertTrue(user.is_valid)
        dct = user.to_mongo()

        async def resolve(document_class, value):
            return value

        user2 = await User.from_mongo(dct, resolve)
        self.assertEqual(user, user2)


if __name__ == '__main__':
    unittest.main(exit=False)
