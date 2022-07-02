from elements._elementBase import ElementBase, docDB


class StorageGroup(ElementBase):
    _attrdef = dict(
        name=ElementBase.addAttr(unique=True, notnone=True),
        desc=ElementBase.addAttr(default='', notnone=True)
    )

    def delete_pre(self):
        docDB.update_many('StorageLocation', {'storage_group_id': self['_id']}, {'$set': {'storage_group_id': None}})
