from unittest import TestCase
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from motorodm import StringField, ObjectIdField

client = AsyncIOMotorClient()

from motorodm import Document


class TestIntegration(TestCase):

    def test_smoke(self):

        class User(Document):
            email = StringField(required=True, unique=True)
            first_name = StringField(db_name='firstName')
            last_name = StringField(db_name='lastName')

        async def run_async(db):
            await User.qs(db).ensure_indices()
            await User.qs(db).drop()

            user = await User(email='rob.blackbourn@example.com', first_name='Rob', last_name='Blackbourn').qs(db).save()
            self.assertTrue(user._id is not None)

            users = await User.qs(db).insert_many(
                User(email='foo@bar.com', first_name='Fred', last_name='Jackson'),
                User(email='grum@bar.com', first_name='Bob', last_name='Thompson'),
            )
            self.assertEqual(len(users), 2)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_async(client.test_motorodm))
