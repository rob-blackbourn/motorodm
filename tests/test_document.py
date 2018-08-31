from motorodm import Document
from motorodm import StringField, ListField


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

user2 = PermissionedUser.from_mongo(user.to_mongo())
assert not user2.is_dirty
assert user2 == user
assert user2.is_valid

print('Done')
