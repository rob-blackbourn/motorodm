import pytest

from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from motorodm import (
    Document,
    StringField,
    ReferenceField,
    ListField,
    DateTimeField
)


def create_client():
    return AsyncIOMotorClient(
        host='localhost',
        port=27017,
        username="root",
        password="password",
        authSource="admin"
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_smoke():
    client = create_client()

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
    client = create_client()

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
    client = create_client()

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
async def test_unique_index():
    client = create_client()

    class User(Document):
        name = StringField(required=True, unique=True)

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)

    try:
        await User.qs(db).ensure_indices()

        await User.qs(db).create(name='Tom')
        await User.qs(db).create(name='Dick')

        try:
            await User.qs(db).create(name='Tom')
            assert False
        except:
            assert True

    finally:
        await db.drop_collection(User.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_unique_compound_index():
    client = create_client()

    class User(Document):
        name = StringField(required=True, unique=True)
        gender = StringField(required=True, unique=True)

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)

    try:
        await User.qs(db).ensure_indices()

        await User.qs(db).create(name='Robin', gender='Male')
        await User.qs(db).create(name='Robin', gender='Female')

        try:
            await User.qs(db).create(name='Robin', gender='Male')
            assert False
        except:
            assert True

    finally:
        await db.drop_collection(User.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get():
    client = create_client()

    class User(Document):
        name = StringField()

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)

    try:
        await User.qs(db).ensure_indices()

        tom = await User.qs(db).create(name='Tom')
        dick = await User.qs(db).create(name='Dick')
        harry = await User.qs(db).create(name='Harry')

        tom1 = await User.qs(db).get(tom._identity)
        assert tom == tom1
        dick1 = await User.qs(db).get(dick._identity)
        assert dick == dick1
        harry1 = await User.qs(db).get(harry._identity)
        assert harry == harry1

    finally:
        await db.drop_collection(User.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_find_one():
    client = create_client()

    class User(Document):
        name = StringField(required=True, unique=True)

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)

    try:
        await User.qs(db).ensure_indices()

        tom = await User.qs(db).create(name='Tom')
        dick = await User.qs(db).create(name='Dick')

        tom1 = await User.qs(db).find_one(name={'$eq': tom.name})
        assert tom == tom1
        dick1 = await User.qs(db).find_one(**{User.name.name: {'$eq': dick.name}})
        assert dick == dick1

        harry = await User.qs(db).find_one(name={'$eq': 'Harry'})
        assert harry is None

    finally:
        await db.drop_collection(User.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_find_in():
    client = create_client()

    class User(Document):
        name = StringField(required=True, unique=True)

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)

    try:
        await User.qs(db).ensure_indices()

        tom = await User.qs(db).create(name='Tom')
        dick = await User.qs(db).create(name='Dick')
        harry = await User.qs(db).create(name='Harry')

        cursor = User.qs(db).find(name={'$in': [tom.name, dick.name]})
        users = [user async for user in cursor]
        assert len(users) == 2
        assert tom in users
        assert dick in users
        assert harry not in users

    finally:
        await db.drop_collection(User.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_find_some():
    client = create_client()

    class User(Document):
        name = StringField(required=True, unique=True)
        gender = StringField(required=True)

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)

    try:
        await User.qs(db).ensure_indices()

        tom = await User.qs(db).create(name='Tom', gender='Male')
        dick = await User.qs(db).create(name='Dick', gender='Male')
        harry = await User.qs(db).create(name='Harry', gender='Male')
        mary = await User.qs(db).create(name='Mary', gender='Female')
        lucy = await User.qs(db).create(name='Lucy', gender='Female')

        males = [user async for user in User.qs(db).find(gender={'$eq': 'Male'})]
        assert len(males) == 3
        assert tom in males
        assert dick in males
        assert harry in males
        females = [user async for user in User.qs(db).find(gender={'$eq': 'Female'})]
        assert len(females) == 2
        assert mary in females
        assert lucy in females

    finally:
        await db.drop_collection(User.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_find_with_and():
    client = create_client()

    class User(Document):
        name = StringField(required=True)
        gender = StringField(required=True)

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)

    try:
        await User.qs(db).ensure_indices()

        male_robin = await User.qs(db).create(name='Robin', gender='Male')
        female_robin = await User.qs(db).create(name='Robin', gender='Female')

        matches = [user async for user in User.qs(db).find(
            **{
                '$and': [
                    {'name': {'$eq': 'Robin'}},
                    {'gender': {'$eq': 'Male'}}
                ]
            })]
        assert len(matches) == 1
        assert male_robin in matches
        assert female_robin not in matches

    finally:
        await db.drop_collection(User.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_find_many():
    client = create_client()

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
    client = create_client()

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

    try:
        user = await User(name='Rob').qs(db).save()
        assert user.created is not None
        assert user.updated is not None
        assert user.created == user.updated

        user.name = 'Tom'
        await user.qs(db).save()
        assert user.updated > user.created
    finally:
        await db.drop_collection(User.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_find_referenced():
    client = create_client()

    class User(Document):
        primary_email = StringField(db_name='primaryEmail', required=True, unique=True)
        password = StringField(required=True)
        secondary_emails = ListField(db_name='secondaryEmails', item_field=StringField())
        given_names = ListField(db_name='givenNames', item_field=StringField())
        family_name = StringField(db_name='familyName')
        nickname = StringField()

    class Permission(Document):
        user = ReferenceField(reference_document_type=User, required=True, unique=True)
        roles = ListField(item_field=StringField(), required=True)

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)
    await db.drop_collection(Permission.__collection__)

    try:
        rob = await User(primary_email='rob@example.com', password='password').qs(db).save()
        robs_permission = await Permission(user=rob, roles=['a', 'b', 'c']).qs(db).save()
        tom = await User(primary_email='tom@example.com', password='password').qs(db).save()
        toms_permission = await Permission(user=tom, roles=['a', 'b', 'c']).qs(db).save()

        both_permissions = [permission async for permission in Permission.qs(db).find(user={'$in': [rob, tom]})]
        assert len(both_permissions) == 2
        assert robs_permission in both_permissions
        assert toms_permission in both_permissions

    finally:
        await db.drop_collection(User.__collection__)
        await db.drop_collection(Permission.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_find_referenced_fake():
    client = create_client()

    class User(Document):
        primary_email = StringField(db_name='primaryEmail', required=True, unique=True)
        password = StringField(required=True)
        secondary_emails = ListField(db_name='secondaryEmails', item_field=StringField())
        given_names = ListField(db_name='givenNames', item_field=StringField())
        family_name = StringField(db_name='familyName')
        nickname = StringField()

    class Permission(Document):
        user = ReferenceField(reference_document_type=User, required=True, unique=True)
        roles = ListField(item_field=StringField(), required=True)

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)
    await db.drop_collection(Permission.__collection__)

    try:
        rob = await User(primary_email='rob@example.com', password='password').qs(db).save()
        robs_permission = await Permission(user=rob, roles=['a', 'b', 'c']).qs(db).save()
        tom = await User(primary_email='tom@example.com', password='password').qs(db).save()
        toms_permission = await Permission(user=tom, roles=['a', 'b', 'c']).qs(db).save()

        fake_users = [
            User(id=rob._identity),
            User(id=tom._identity)
        ]
        both_permissions = [permission async for permission in Permission.qs(db).find(user={'$in': fake_users})]
        assert len(both_permissions) == 2
        assert robs_permission in both_permissions
        assert toms_permission in both_permissions

    finally:
        await db.drop_collection(User.__collection__)
        await db.drop_collection(Permission.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_distinct():
    client = create_client()

    class User(Document):
        name = StringField(db_name='primaryEmail', required=True, unique=True)
        gender = StringField(required=True)

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)

    try:
        rob_male = await User(name='rob', gender='male').qs(db).save()
        rob_female = await User(name='rob', gender='female').qs(db).save()
        tom_male = await User(name='tom', gender='male').qs(db).save()
        tom_female = await User(name='tom', gender='female').qs(db).save()

        cursor = User.qs(db).find()
        results = await cursor.distinct('gender')
        assert set(results) == {'male', 'female'}

    finally:
        await db.drop_collection(User.__collection__)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_skip_and_limit():
    client = create_client()

    class User(Document):
        name = StringField(db_name='primaryEmail', required=True, unique=True)

    db = client.test_motorodm
    await db.drop_collection(User.__collection__)

    try:
        for i in range(100):
            await User(name=f'user{i}').qs(db).save()

        cursor = User.qs(db).find().skip(10).limit(10)
        results = [user async for user in cursor]
        assert len(results) == 10

    finally:
        await db.drop_collection(User.__collection__)
