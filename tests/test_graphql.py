import asyncio
import unittest
from motorodm import Document, StringField, ObjectIdField
import graphene
from graphql.execution.executors.asyncio import AsyncioExecutor
from motorodm.graphene import MotorOdmObjectType
from motor.motor_asyncio import AsyncIOMotorClient
from tests.utils import run_async


class TestGraphQL(unittest.TestCase):

    def setUp(self):
        self.client = AsyncIOMotorClient()

    @run_async
    async def test_smoke(self):

        class UserModel(Document):
            __collection__ = 'user'
            email = StringField(required=True, unique=True)
            first_name = StringField(db_name='firstName')
            last_name = StringField(db_name='lastName')

        db = self.client.test_motorodm

        await UserModel.qs(db).drop()
        await UserModel.qs(db).ensure_indices()

        rob = await UserModel(email='rob.blackbourn@example.com', first_name='Rob', last_name='Blackbourn').qs(db).save()
        ann = await UserModel(email='ann.jones@example.com', first_name='Ann', last_name='Jones').qs(db).save()

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
            user = graphene.Field(
                User, email=graphene.String(), id=graphene.ID())

            async def resolve_users(self, info, email=None):
                cursor = UserModel.qs(info.context['db']).find()
                # return await cursor.to_list(100)
                return [user async for user in cursor]

            async def resolve_user(self, info, **kwargs):
                return await UserModel.qs(info.context['db']).find_one(**kwargs)

        class Mutation(graphene.ObjectType):
            create_user = CreateUser.Field()

        schema = graphene.Schema(query=Query, mutation=Mutation)

        query = '''
            query {
                users {
                    id,
                    firstName,
                    lastName
                }
            }
        '''

        query_result = await schema.execute(
            query, context={'db': db}, executor=AsyncioExecutor(), return_promise=True)
        print(query_result)

        mutation = '''
            mutation testMutation {
                createUser(email: "john.doe@example.com", firstName: "John", lastName: "Doe") {
                    id
                    email
                    firstName
                    lastName
                }
            }
        '''

        mutation_result = await schema.execute(
            mutation, context={'db': db}, executor=AsyncioExecutor(), return_promise=True)
        print(mutation_result)

        query2 = '''
            query {
                user(email: "rob.blackbourn@example.com") {
                    id
                    firstName
                    lastName
                }
            }
        '''

        query2_result = await schema.execute(
            query2, context={'db': db}, executor=AsyncioExecutor(), return_promise=True)
        print(query2_result)

        query3 = '''
            query getUser($email: String!) {
                user(email: $email) {
                    id
                    firstName
                    lastName
                }
            }
        '''

        query3_result = await schema.execute(
            query3, context={'db': db}, executor=AsyncioExecutor(), return_promise=True, variables={'email': "rob.blackbourn@example.com"})
        print(query3_result)

        query4 = '''
            query getUser($id: ID!) {
                user(id: $id) {
                    id
                    firstName
                    lastName
                }
            }
        '''

        query4_result = await schema.execute(
            query4, context={'db': db}, executor=AsyncioExecutor(), return_promise=True, variables={'id': ann.id})
        print(query4_result)


if __name__ == '__main__':
    unittest.main(exit=False)
