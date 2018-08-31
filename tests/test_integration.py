from unittest import TestCase
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from motorodm import StringField, ObjectIdField, ReferenceField, ListField

client = AsyncIOMotorClient()

from motorodm import Document
from .utils import run_async


class TestIntegration(TestCase):

    @run_async
    async def test_smoke(self):

        class User(Document):
            email = StringField(required=True, unique=True)
            first_name = StringField(db_name='firstName')
            last_name = StringField(db_name='lastName')

        db = client.test_motorodm

        await User.qs(db).ensure_indices()
        await User.qs(db).drop()

        user = await User(email='rob.blackbourn@example.com', first_name='Rob', last_name='Blackbourn').qs(db).save()
        self.assertTrue(user._id is not None)

        users = await User.qs(db).insert_many(
            User(email='foo@bar.com', first_name='Fred', last_name='Jackson'),
            User(email='grum@bar.com', first_name='Bob', last_name='Thompson'),
        )
        self.assertEqual(len(users), 2)

    @run_async
    async def test_reference_field(self):

        class User(Document):
            name = StringField()

        class Post(Document):
            user = ReferenceField(User)
            title = StringField()
            body = StringField()

        db = client.test_motorodm

        await User.qs(db).drop()
        await Post.qs(db).drop()

        rob = await User(name='Rob').qs(db).save()
        post = await Post(user=rob, title='My Post', body='Words of wisdom').qs(db).save()

        post1 = await Post.qs(db).get(post._id)
        self.assertEqual(post, post1)

    @run_async
    async def test_list_reference_field(self):

        class User(Document):
            name = StringField()

        class Updaters(Document):
            users = ListField(ReferenceField(User))

        db = client.test_motorodm

        await User.qs(db).drop()
        await Updaters.qs(db).drop()

        rob = await User(name='Rob').qs(db).save()
        tom = await User(name='Tom').qs(db).save()
        updaters = await Updaters(users=[rob, tom]).qs(db).save()

        updaters1 = await Updaters.qs(db).get(updaters._id)
        self.assertEqual(updaters, updaters1)
