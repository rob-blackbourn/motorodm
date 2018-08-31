class DocumentIterator:

    def __init__(self, cursor, document_class):
        self.cursor = cursor
        self.document_class = document_class

    def __aiter__(self):
        return self

    async def __anext__(self):
        if await self.cursor.fetch_next():
            data = self.cursor.next_object()
            return self.document_class.from_mongo(data)
        else:
            raise StopAsyncIteration

    async def distinct(self):
        return await self.cursor.distinct()

    def limit(self, n):
        self.cursor.limit(n)

    def skip(self, n):
        self.cursor.skip(n)

    def sort(self, key_or_list, direction=None):
        self.cursor.sort(key_or_list, direction)

    async def to_list(self, length):
        return await self.cursor.to_list(length)

    @property
    def alive(self):
        return self.cursor.alive
