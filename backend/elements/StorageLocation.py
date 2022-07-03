from elements._elementBase import ElementBase, docDB


class StorageLocation(ElementBase):
    _attrdef = dict(
        name=ElementBase.addAttr(notnone=True),
        desc=ElementBase.addAttr(default='', notnone=True),
        parent_storage_location_id=ElementBase.addAttr(),
        storage_group_id=ElementBase.addAttr()
    )

    def validate(self):
        errors = dict()
        if self['parent_storage_location_id'] is not None and self['parent_storage_location_id'] == self['_id']:
            errors['parent_storage_location_id'] = "Can't be the own id"
        elif self['parent_storage_location_id'] is not None and not docDB.exists(self.__class__.__name__, self['parent_storage_location_id']):
            errors['parent_storage_location_id'] = f"There is no StorageLocation with id '{self['parent_storage_location_id']}"
        if self['storage_group_id'] is not None and not docDB.exists('StorageGroup', self['storage_group_id']):
            errors['storage_group_id'] = f"There is no StorageGroup with id '{self['storage_group_id']}"
        return errors

    def delete_pre(self):
        from elements import PartLocation
        docDB.update_many(self.__class__.__name__, {'parent_storage_location_id': self['_id']}, {'$set': {'parent_storage_location_id': None}})
        for pl in docDB.search_many('PartLocation', {'storage_location_id': self['_id']}):
            pl = PartLocation(pl)
            pl.delete()
