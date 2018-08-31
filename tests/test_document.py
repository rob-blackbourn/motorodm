from unittest import TestCase
from asyncio import Future

from motorodm import Document
from motorodm import StringField, ListField, ReferenceField
from bson import ObjectId

from .utils import run_async


class TestDocument(TestCase):

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

        id = ObjectId()
        user = User(_id=id, name='Fred')
        self.assertTrue(user.is_valid)
        self.assertEqual(id, user._identity)

        id2 = ObjectId()
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

        user = User(_id=ObjectId(), name='Rob')
        post = Post(_id=ObjectId(), user=user,
                    title='My Post', body='Words of wisdom')

        self.assertTrue(post.is_valid)
        dct = post.to_mongo()
        self.assertIn('user', dct)

        async def resolve(document_class, value):
            return value

        post2 = await Post.from_mongo(dct, resolve)
        print('Hello!!!!')
        self.assertEqual(post, post2)
