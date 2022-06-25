from elements._elementBase import ElementBase, docDB


class MountingStyle(ElementBase):
    _attrdef = dict(
        name=ElementBase.addAttr(unique=True, notnone=True),
        desc=ElementBase.addAttr(default='')
    )

    def delete_pre(self):
        docDB.update_many('Footprint', {'mounting_style_id': self['_id']}, {'$set': {'mounting_style_id': None}})
