class InstanceQuerySet(object):

    def __init__(self, document, db):
        self.document = document
        self.db = db

    @property
    def collection(self):
        return self.db[self.document.__collection__]

    async def save(self):
        data = self.document.to_mongo()
        id = data.pop('_id', None)
        if id:
            await self.collection.update_one({'_id': id}, {'$set': data})
        else:
            ret = await self.collection.insert_one(data)
            self.document._identity = ret.inserted_id

        self.document._make_clean()

        return self.document

    async def delete(self):
        await self.collection.delete_one({'_id': self.document._identity})

    async def update(self):
        data = self.document.to_mongo()
        id = data.pop(self.document._db_name_map['_id'])
        updates = {
            db_name: data[db_name]
            for db_name in map(
                lambda field_name: self.document._db_name_map[field_name],
                self.document._dirty_fields
            )
        }
        await self.collection.update_one({'_id': id}, {'$set': updates})

        self.document._make_clean()
