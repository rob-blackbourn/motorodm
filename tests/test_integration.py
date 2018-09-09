import unittest
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from motorodm import (
    Document,
    StringField,
    ObjectIdField,
    ReferenceField,
    ListField,
    DateTimeField
)

from tests.utils import run_async


class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.client = AsyncIOMotorClient()

    @run_async
    async def test_smoke(self):

        class User(Document):
            email = StringField(required=True, unique=True)
            first_name = StringField(db_name='firstName')
            last_name = StringField(db_name='lastName')

        db = self.client.test_motorodm
        await db.drop_collection(User.__collection__)

        try:
            await User.qs(db).ensure_indices()

            user = await User(email='rob.blackbourn@example.com', first_name='Rob', last_name='Blackbourn').qs(db).save()
            self.assertTrue(user._identity is not None)

            users = await User.qs(db).insert_many(
                User(email='foo@bar.com', first_name='Fred', last_name='Jackson'),
                User(email='grum@bar.com', first_name='Bob', last_name='Thompson'),
            )
            self.assertEqual(len(users), 2)
        finally:
            await db.drop_collection(User.__collection__)

    @run_async
    async def test_reference_field(self):

        class User(Document):
            name = StringField()

        class Post(Document):
            user = ReferenceField(User)
            title = StringField()
            body = StringField()

        db = self.client.test_motorodm
        await db.drop_collection(User.__collection__)
        await db.drop_collection(Post.__collection__)

        try:
            rob = await User(name='Rob').qs(db).save()
            post = await Post(user=rob, title='My Post', body='Words of wisdom').qs(db).save()

            post1 = await Post.qs(db).get(post._identity)
            self.assertEqual(post, post1)
        finally:
            await db.drop_collection(User.__collection__)
            await db.drop_collection(Post.__collection__)

    @run_async
    async def test_list_reference_field(self):

        class User(Document):
            name = StringField()

        class Updaters(Document):
            users = ListField(ReferenceField(User))

        db = self.client.test_motorodm
        await db.drop_collection(User.__collection__)
        await db.drop_collection(Updaters.__collection__)

        try:
            rob = await User(name='Rob').qs(db).save()
            tom = await User(name='Tom').qs(db).save()
            updaters = await Updaters(users=[rob, tom]).qs(db).save()

            updaters1 = await Updaters.qs(db).get(updaters._identity)
            self.assertEqual(updaters, updaters1)
        finally:
            await db.drop_collection(User.__collection__)
            await db.drop_collection(Updaters.__collection__)

    @run_async
    async def test_find_many(self):

        class User(Document):
            name = StringField()

        db = self.client.test_motorodm
        await db.drop_collection(User.__collection__)

        try:
            await User.qs(db).ensure_indices()

            await User.qs(db).create(name='Tom')
            await User.qs(db).create(name='Dick')
            await User.qs(db).create(name='Harry')

            users = {user.name: user async for user in User.qs(db).find()}
            self.assertEqual(3, len(users))
            self.assertTrue('Tom' in users)
            self.assertTrue('Dick' in users)
            self.assertTrue('Harry' in users)
        finally:
            await db.drop_collection(User.__collection__)

    @run_async
    async def test_before_hooks(self):

        class User(Document):
            name = StringField()
            created = DateTimeField()
            updated = DateTimeField()

            def before_create(self):
                self.created = self.updated = datetime.utcnow()

            def before_update(self):
                self.updated = datetime.utcnow()

        db = self.client.test_motorodm
        await db.drop_collection(User.__collection__)

        user = await User(name='Rob').qs(db).save()
        self.assertIsNotNone(user.created)
        self.assertIsNotNone(user.updated)
        self.assertEqual(user.created, user.updated)

        user.name = 'Tom'
        await user.qs(db).save()
        self.assertGreater(user.updated, user.created)

        await db.drop_collection(User.__collection__)


if __name__ == '__main__':
    unittest.main(exit=False)
