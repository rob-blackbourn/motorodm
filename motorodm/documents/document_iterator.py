import pymongo


class DocumentIterator:

    def __init__(self, cursor, document_class, db):
        self.cursor = cursor
        self.document_class = document_class
        self.db = db


    def __aiter__(self):
        return self


    async def __anext__(self):
        if await self.cursor.fetch_next:
            data = self.cursor.next_object()
            return await self.document_class.from_mongo(data, self.resolve)
        else:
            raise StopAsyncIteration


    async def distinct(self, key):
        return await self.cursor.distinct(key)


    def limit(self, n):
        self.cursor.limit(n)
        return self


    def skip(self, n):
        self.cursor.skip(n)
        return self


    def sort(self, key_or_list, direction=pymongo.ASCENDING):
        self.cursor.sort(key_or_list, direction)
        return self


    async def to_list(self, length):
        return [await self.document_class.from_mongo(item, self.resolve) for item in await self.cursor.to_list(length)]


    async def resolve(self, document_class, value):
        value = await document_class.qs(self.db).get(value)
        return value


    @property
    def alive(self):
        return self.cursor.alive
