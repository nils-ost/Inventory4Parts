from elements._elementBase import ElementBase, docDB


class Unit(ElementBase):
    _attrdef = dict(
        name=ElementBase.addAttr(unique=True, notnone=True),
        desc=ElementBase.addAttr(default=''),
        default=ElementBase.addAttr(type=bool, default=False, notnone=True)
    )

    def save_pre(self):
        if len(self.__class__.all()) == 0:
            self['default'] = True
        if self['default']:
            docDB.update_many(self.__class__.__name__, {'default': True}, {'$set': {'default': False}})

    def delete_post(self):
        if docDB.search_one(self.__class__.__name__, {'default': True}) is None:
            someunit = docDB.search_one(self.__class__.__name__, {})
            if someunit is not None:
                someunit = Unit(someunit)
                someunit['default'] = True
                someunit.save()
