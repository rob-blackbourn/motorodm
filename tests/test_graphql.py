import asyncio
import unittest
from motorodm import Document, StringField, ObjectIdField
import graphene
from graphql.execution.executors.asyncio import AsyncioExecutor
from motorodm.graphene import MotorOdmObjectType
from motor.motor_asyncio import AsyncIOMotorClient


class TestGraphQL(unittest.TestCase):

    def setUp(self):
        self.client = AsyncIOMotorClient()

    def test_smoke(self):

        class UserModel(Document):
            email = StringField(required=True, unique=True)
            first_name = StringField(db_name='firstName')
            last_name = StringField(db_name='lastName')

        async def create(db):
            await UserModel.qs(db).drop()
            await UserModel.qs(db).ensure_indices()

            rob = await UserModel(email='rob.blackbourn@example.com', first_name='Rob', last_name='Blackbourn').qs(db).save()
            ann = await UserModel(email='ann.jones@example.com', first_name='Ann', last_name='Jones').qs(db).save()

            return [rob, ann]

        class User(MotorOdmObjectType):
            class Meta:
                model = UserModel

        class CreateUser(graphene.Mutation):

            Output = User

            class Arguments:
                email = graphene.String(required=True)
                first_name = graphene.String(required=True)
                last_name = graphene.String(required=True)

            async def mutate(self, info, **kwargs):
                user = await UserModel(**kwargs).qs(info.context['db']).save()
                return user

        class Query(graphene.ObjectType):
            users = graphene.List(User)

            async def resolve_users(self, info, email=None):
                cursor = UserModel.qs(info.context['db']).find()
                # return await cursor.to_list(100)
                return [user async for user in cursor]

        class Mutation(graphene.ObjectType):
            create_user = CreateUser.Field()

        schema = graphene.Schema(query=Query, mutation=Mutation)

        db = self.client.test_motorodm
        loop = asyncio.get_event_loop()
        users = loop.run_until_complete(create(db))

        query = '''
            query {
                users {
                    id,
                    firstName,
                    lastName
                }
            }
        '''

        query_result = schema.execute(
            query, context={'db': db}, executor=AsyncioExecutor(loop=loop))
        print(query_result)

        mutation = '''
            mutation testMutation {
                createUser(email: "john.doe@example.com", firstName: "John", lastName: "Doe") {
                    email
                    firstName
                    lastName
                }
            }
        '''

        mutation_result = schema.execute(
            mutation, context={'db': db}, executor=AsyncioExecutor(loop=loop))
        print(mutation_result)

        query2 = '''
            query {
                users(email: "rob.blackbourn@example.com") {
                    id
                    firstName
                    lastName
                }
            }
        '''

        query2_result = schema.execute(
            query2, context={'db': db}, executor=AsyncioExecutor(loop=loop))
        print(query2_result)


if __name__ == '__main__':
    unittest.main(exit=False)
