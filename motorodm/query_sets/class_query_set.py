from .instance_query_set import InstanceQuerySet
from ..documents.document_iterator import DocumentIterator


class ClassQuerySet(object):

    def __init__(self, document_class, db):
        self.document_class = document_class
        self.db = db

    @property
    def collection(self):
        return self.db[self.document_class.__collection__]

    async def resolve(self, document_class, value):
        qs = document_class.qs(self.db)
        document = await qs.get(value)
        return document

    async def create(self, **kwargs):
        document = self.document_class(**kwargs)
        query_set = InstanceQuerySet(document, self.db)
        return await query_set.create()

    async def get(self, id):
        kwargs = {self.document_class._db_name_map['_id']: id}
        return await self.find_one(**kwargs)

    async def find_one(self, **kwargs):
        query = self._to_query(**kwargs)
        result = await self.collection.find_one(query)
        if not result:
            return None
        return await self.document_class.from_mongo(result, self.resolve)

    def find(self, **kwargs):
        query = self._to_query(**kwargs)
        return DocumentIterator(self.collection.find(query), self.document_class, self.db)

    def _to_query(self, **kwargs):
        return {
            self.document_class._fields[name].db_name: self.document_class._fields[name].to_mongo(
                value)
            for name, value in kwargs.items()
        }

    async def drop(self):
        await self.collection.drop()

    async def ensure_indices(self):
        keys = [
            (
                self.document_class._db_name_map[field_name],
                self.document_class._fields[field_name].sort_order
            )
            for field_name in self.document_class._indices
        ]
        if len(keys) > 0:
            await self.collection.create_index(keys)

    async def insert_many(self, *documents):
        data = [document.to_mongo() for document in documents]
        ret = await self.collection.insert_many(data)
        for id, document in zip(ret.inserted_ids, documents):
            document._identity = str(id)
        return documents
