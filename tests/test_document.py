import pytest

from asyncio import Future
from datetime import datetime

from motorodm import (
    Document,
    EmbeddedDocument,
    StringField,
    ListField,
    ReferenceField,
    EmbeddedDocumentField,
    DateTimeField
)
from bson import ObjectId


@pytest.mark.unit
@pytest.mark.asyncio
async def test_smoke():
    class User(Document):
        first_name = StringField(db_name='firstName')
        last_name = StringField(db_name='lastName')

    class PermissionedUser(User):
        roles = ListField(item_field=StringField())

    assert PermissionedUser.first_name.name == "first_name"
    assert PermissionedUser.first_name.db_name == "firstName"
    assert PermissionedUser.last_name.name == "last_name"
    assert PermissionedUser.last_name.db_name == "lastName"
    assert PermissionedUser.roles.name == "roles"
    assert PermissionedUser.roles.db_name == "roles"

    user = PermissionedUser(
        first_name='Rob',
        last_name='Blackbourn',
        roles=['a', 'b', 'c'])

    assert not user.is_dirty
    assert user.first_name == 'Rob'
    assert user.last_name == 'Blackbourn'
    assert user.roles == ['a', 'b', 'c']
    assert user.is_valid

    user.first_name = 'Thomas'
    assert user.first_name == 'Thomas'
    assert user.is_dirty
    user._make_clean()
    assert not user.is_dirty

    user2 = await PermissionedUser.from_mongo(user.to_mongo(), None)
    assert not user2.is_dirty
    assert user2 == user
    assert user2.is_valid


@pytest.mark.unit
def test_identity():
    class User(Document):
        name = StringField()

    id = str(ObjectId())
    user = User(id=id, name='Fred')
    assert user.is_valid
    assert id == user._identity

    id2 = str(ObjectId())
    user._identity = id2
    assert id2 == user._identity


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reference_field():
    class User(Document):
        name = StringField()

    class Post(Document):
        user = ReferenceField(User)
        title = StringField()
        body = StringField()

    user = User(id=str(ObjectId()), name='Rob')
    post = Post(id=str(ObjectId()), user=user,
                title='My Post', body='Words of wisdom')

    assert post.is_valid
    dct = post.to_mongo()
    assert 'user' in dct

    async def resolve(document_class, value):
        return user

    post2 = await Post.from_mongo(dct, resolve)
    assert post == post2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_embedded_document():
    class Address(EmbeddedDocument):
        street = StringField()
        town = StringField()

    class User(Document):
        name = StringField()
        address = EmbeddedDocumentField(Address)

    user = User(name='Fred', address=Address(
        street='1 Main Street', town='Atlantis'))

    assert user.is_valid
    dct = user.to_mongo()

    async def resolve(document_class, value):
        return value

    user2 = await User.from_mongo(dct, resolve)
    assert user == user2


@pytest.mark.unit
def test_before_set():
    class User(Document):
        name = StringField(before_set=lambda x: x.upper())

    user = User(name='fred')
    assert user.name == 'FRED'
