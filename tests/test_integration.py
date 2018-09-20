import pytest

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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_smoke():
    client = AsyncIOMotorClient()

    class User(Document):
        email = StringField(required=True, unique=True)
        first_name = StringField(db_name='firstName')
        last_name = StringField(db_name='lastName')

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)

    try:
        await User.qs(db).ensure_indices()

        user = await User(email='rob.blackbourn@example.com', first_name='Rob', last_name='Blackbourn').qs(db).save()
        assert user._identity is not None

        users = await User.qs(db).insert_many(
            User(email='foo@bar.com', first_name='Fred', last_name='Jackson'),
            User(email='grum@bar.com', first_name='Bob', last_name='Thompson'),
        )
        assert len(users) == 2
    finally:
        await db.drop_collection(User.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_reference_field():
    client = AsyncIOMotorClient()

    class User(Document):
        name = StringField()

    class Post(Document):
        user = ReferenceField(User)
        title = StringField()
        body = StringField()

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)
    await db.drop_collection(Post.__collection__)

    try:
        rob = await User(name='Rob').qs(db).save()
        post = await Post(user=rob, title='My Post', body='Words of wisdom').qs(db).save()

        post1 = await Post.qs(db).get(post._identity)
        assert post == post1
    finally:
        await db.drop_collection(User.__collection__)
        await db.drop_collection(Post.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_reference_field():
    client = AsyncIOMotorClient()

    class User(Document):
        name = StringField()

    class Updaters(Document):
        users = ListField(ReferenceField(User))

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)
    await db.drop_collection(Updaters.__collection__)

    try:
        rob = await User(name='Rob').qs(db).save()
        tom = await User(name='Tom').qs(db).save()
        updaters = await Updaters(users=[rob, tom]).qs(db).save()

        updaters1 = await Updaters.qs(db).get(updaters._identity)
        updaters == updaters1
    finally:
        await db.drop_collection(User.__collection__)
        await db.drop_collection(Updaters.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_find_many():
    client = AsyncIOMotorClient()

    class User(Document):
        name = StringField()

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)

    try:
        await User.qs(db).ensure_indices()

        await User.qs(db).create(name='Tom')
        await User.qs(db).create(name='Dick')
        await User.qs(db).create(name='Harry')

        users = {user.name: user async for user in User.qs(db).find()}
        assert 3 == len(users)
        assert 'Tom' in users
        assert 'Dick' in users
        assert 'Harry' in users
    finally:
        await db.drop_collection(User.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_before_hooks():
    client = AsyncIOMotorClient()

    class User(Document):
        name = StringField()
        created = DateTimeField()
        updated = DateTimeField()

        def before_create(self):
            self.created = self.updated = datetime.utcnow()

        def before_update(self):
            self.updated = datetime.utcnow()

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)

    user = await User(name='Rob').qs(db).save()
    assert user.created is not None
    assert user.updated is not None
    assert user.created == user.updated

    user.name = 'Tom'
    await user.qs(db).save()
    assert user.updated > user.created

    await db.drop_collection(User.__collection__)
