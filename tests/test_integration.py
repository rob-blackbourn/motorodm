import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from motorodm import StringField, ObjectIdField

client = AsyncIOMotorClient()

from motorodm import Document


class User(Document):
    email = StringField(required=True, unique=True)
    first_name = StringField(db_name='firstName')
    last_name = StringField(db_name='lastName')


async def run_async(db):
    print('index')
    await User.qs(db).ensure_indices()
    print('drop')
    await User.qs(db).drop()
    print('save')
    user = await User(email='rob.blackbourn@example.com', first_name='Rob', last_name='Blackbourn').qs(db).save()
    assert user._id is not None
    print('bulk insert')
    users = await User.qs(db).insert_many(
        User(email='foo@bar.com', first_name='Fred', last_name='Jackson'),
        User(email='grum@bar.com', first_name='Bob', last_name='Thompson'),
    )
    assert len(users) == 2
    print("Done")


loop = asyncio.get_event_loop()
loop.run_until_complete(run_async(client.test_motorodm))
