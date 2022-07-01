from elements._elementBase import ElementBase, docDB


class Category(ElementBase):
    _attrdef = dict(
        name=ElementBase.addAttr(notnone=True),
        desc=ElementBase.addAttr(default='', notnone=True),
        parent_category_id=ElementBase.addAttr()
    )

    def validate(self):
        errors = dict()
        if self['parent_category_id'] is not None and self['parent_category_id'] == self['_id']:
            errors['parent_category_id'] = "Can't be the own id"
        elif self['parent_category_id'] is not None and not docDB.exists(self.__class__.__name__, self['parent_category_id']):
            errors['parent_category_id'] = f"There is no Category with id '{self['parent_category_id']}"
        return errors

    def delete_pre(self):
        if docDB.search_one('Part', {'category_id': self['_id']}) is not None:
            return {'error': f"{repr(self)} can't be deleted as at least one Part is associated"}
        docDB.update_many(self.__class__.__name__, {'parent_category_id': self['_id']}, {'$set': {'parent_category_id': None}})
