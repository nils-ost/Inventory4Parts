from elements._elementBase import ElementBase, docDB
import time


class Order(ElementBase):
    _attrdef = dict(
        part_id=ElementBase.addAttr(notnone=True),
        distributor_id=ElementBase.addAttr(),
        created_at=ElementBase.addAttr(type=int),
        amount=ElementBase.addAttr(type=int, default=1, notnone=True),
        price=ElementBase.addAttr(type=float, default=0.0, notnone=True)
    )

    def validate(self):
        errors = dict()
        if not docDB.exists('Part', self['part_id']):
            errors['part_id'] = f"There is no Part with id '{self['part_id']}'"
        if self['distributor_id'] is not None and not docDB.exists('Distributor', self['distributor_id']):
            errors['distributor_id'] = f"There is no Distributor with id '{self['distributor_id']}'"
        if self['amount'] < 1:
            errors['amount'] = 'Needs to be one or more'
        if self['price'] < 0:
            errors['price'] = "Can't be negative"
        if self['created_at'] is not None and self['created_at'] < 0:
            errors['created_at'] = "Can't be negative"
        return errors

    def save_pre(self):
        if self['created_at'] is None:
            self['created_at'] = int(time.time())

    def completed(self):
        return False

    def json(self):
        result = super().json()
        result['completed'] = self.completed()
        return result
