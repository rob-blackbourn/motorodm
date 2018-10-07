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
        kwargs = {self.document_class._db_name_map['_id']: {'$eq': id}}
        value = await self.find_one(**kwargs)
        return value

    async def find_one(self, **kwargs):
        query = self._to_query(**kwargs)
        result = await self.collection.find_one(query)
        if not result:
            return None
        value = await self.document_class.from_mongo(result, self.resolve)
        return value

    def find(self, **kwargs):
        query = self._to_query(**kwargs)
        return DocumentIterator(self.collection.find(query), self.document_class, self.db)

    async def count_documents(self, **kwargs):
        query = self._to_query(**kwargs)
        return await self.collection.count_documents(query)

    def _to_query_op(self, field, operation):
        if isinstance(operation, dict):
            query = {}
            for operator, value in operation.items():
                if operator in (
                        '$exists', '$type', '$search', '$language', '$caseSensitive', '$diacriticSensitive', '$size',
                        '$regex', '$options', '$mod'):
                    query[operator] = value
                elif operator in ('$in', '$nin', '$all'):
                    query[operator] = [field.to_mongo(item) for item in value]
                else:
                    query[operator] = field.to_mongo(value)
            return query
        else:
            return operation

    def _to_query_clause(self, key, value):
        if key in ('$and', '$or', '$nor', '$elemMatch', '$text', '$expr'):
            return key, [self._to_query(**item) for item in value]
        elif key in ('$not'):
            return key, self._to_query(**value)
        else:
            return self.document_class._fields[key].db_name, self._to_query_op(self.document_class._fields[key], value)

    def _to_query(self, **kwargs):
        return dict(self._to_query_clause(k, v) for k, v in kwargs.items())

    async def drop(self):
        await self.collection.drop()

    async def ensure_indices(self):
        keys = [
            (
                self.document_class._fields[field_name].db_name,
                self.document_class._fields[field_name].sort_order
            )
            for field_name in self.document_class._indices
        ]
        if len(keys) > 0:
            await self.collection.create_index(keys, unique=True)

    async def insert_many(self, *documents):
        data = [document.to_mongo() for document in documents]
        ret = await self.collection.insert_many(data)
        for id, document in zip(ret.inserted_ids, documents):
            document._identity = str(id)
        return documents
