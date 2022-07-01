from elements._elementBase import ElementBase, docDB


class PartDistributor(ElementBase):
    _attrdef = dict(
        part_id=ElementBase.addAttr(notnone=True),
        distributor_id=ElementBase.addAttr(notnone=True),
        desc=ElementBase.addAttr(default='', notnone=True),
        order_no=ElementBase.addAttr(default='', notnone=True),
        url=ElementBase.addAttr(default='', notnone=True),
        pkg_price=ElementBase.addAttr(type=float, default=0.0, notnone=True),
        pkg_units=ElementBase.addAttr(type=int, default=0, notnone=True),
        preferred=ElementBase.addAttr(type=bool, default=False, notnone=True)
    )

    def validate(self):
        errors = dict()
        if not docDB.exists('Part', self['part_id']):
            errors['part_id'] = f"There is no Part with id '{self['part_id']}'"
        if not docDB.exists('Distributor', self['distributor_id']):
            errors['distributor_id'] = f"There is no Distributor with id '{self['distributor_id']}'"
        return errors

    def save_pre(self):
        if len(self.__class__.all()) == 0:
            self['preferred'] = True
        if self['preferred']:
            docDB.update_many(self.__class__.__name__, {'preferred': True}, {'$set': {'preferred': False}})

    def delete_post(self):
        if docDB.search_one(self.__class__.__name__, {'preferred': True}) is None:
            somepd = docDB.search_one(self.__class__.__name__, {})
            if somepd is not None:
                somepd = PartDistributor(somepd)
                somepd['preferred'] = True
                somepd.save()
