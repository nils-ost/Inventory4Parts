from elements._elementBase import ElementBase, docDB


class PartLocation(ElementBase):
    _attrdef = dict(
        part_id=ElementBase.addAttr(notnone=True),
        storage_location_id=ElementBase.addAttr(notnone=True),
        desc=ElementBase.addAttr(default='', notnone=True),
        default=ElementBase.addAttr(type=bool, default=False, notnone=True)
    )

    def validate(self):
        errors = dict()
        if not docDB.exists('Part', self['part_id']):
            errors['part_id'] = f"There is no Part with id '{self['part_id']}'"
        if not docDB.exists('StorageLocation', self['storage_location_id']):
            errors['storage_location_id'] = f"There is no StorageLocation with id '{self['storage_location_id']}'"
        return errors

    def save_pre(self):
        if len(self.__class__.all()) == 0:
            self['default'] = True
        if self['default']:
            docDB.update_many(self.__class__.__name__, {'default': True}, {'$set': {'default': False}})

    def delete_post(self):
        if docDB.search_one(self.__class__.__name__, {'default': True}) is None:
            somepl = docDB.search_one(self.__class__.__name__, {})
            if somepl is not None:
                somepl = PartLocation(somepl)
                somepl['default'] = True
                somepl.save()

    def stock_level(self):
        return 0

    def json(self):
        result = super().json()
        result['stock_level'] = self.stock_level()
        return result
