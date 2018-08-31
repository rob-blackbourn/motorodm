class InstanceQuerySet(object):

    def __init__(self, document, db):
        self.document = document
        self.db = db
        self.id_field_name = document._db_name_map['_id']

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
            setattr(self.document, self.id_field_name, ret.inserted_id)

        self.document._make_clean()

        return self.document

    async def delete(self):
        await self.collection.delete_one({'_id': getattr(self.document, self.id_field_name, None)})

    async def update(self):
        data = self.document.to_mongo()
        id = data.pop(self.id_field_name)
        updates = {
            db_name: data[db_name]
            for db_name in map(
                lambda field_name: self.document._db_name_map[field_name],
                self.document._dirty_fields
            )
        }
        await self.collection.update_one({'_id': id}, {'$set': updates})

        self.document._make_clean()
