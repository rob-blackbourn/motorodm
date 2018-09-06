import asyncio
import unittest
from motorodm import Document, StringField
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

        db = self.client.test_motorodm

        async def create():
            await UserModel.qs(db).ensure_indices()
            await UserModel.qs(db).drop()

            rob = await UserModel(email='rob.blackbourn@example.com', first_name='Rob', last_name='Blackbourn').qs(db).save()
            ann = await UserModel(email='ann.jones@example.com', first_name='Ann', last_name='Jones').qs(db).save()

        class User(MotorOdmObjectType):
            class Meta:
                model = UserModel

            @staticmethod
            async def create(args, context):
                return await UserModel(**args).qs(db).save()

        class CreateUser(graphene.Mutation):

            Output = User

            class Arguments:
                email = graphene.String(required=True)
                first_name = graphene.String(required=True)
                last_name = graphene.String(required=True)

            async def mutate(self, *context, **kwargs):
                user = await UserModel(**kwargs).qs(db).save()
                return user

        class Query(graphene.ObjectType):
            users = graphene.List(User)

            async def resolve_users(self, info):
                cursor = UserModel.qs(db).find()
                # return await cursor.to_list(100)
                return [user async for user in cursor]

        class Mutation(graphene.ObjectType):
            create_user = CreateUser.Field()

        schema = graphene.Schema(query=Query, mutation=Mutation)

        query = '''
            query {
                users {
                    firstName,
                    lastName
                }
            }
        '''

        mutation = '''
            mutation testMutation {
                createUser(email: "john.doe@example.com", firstName: "John", lastName: "Doe") {
                    email
                    firstName
                    lastName
                }
            }
        '''

        loop = asyncio.get_event_loop()
        loop.run_until_complete(create())
        query_result = schema.execute(
            query, executor=AsyncioExecutor(loop=loop))
        print(query_result)
        mutation_result = schema.execute(
            mutation, executor=AsyncioExecutor(loop=loop))
        print(mutation_result)


if __name__ == '__main__':
    unittest.main(exit=False)
