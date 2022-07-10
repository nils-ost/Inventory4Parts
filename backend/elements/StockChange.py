from elements._elementBase import ElementBase, docDB
import time
from decimal import Decimal


class StockChange(ElementBase):
    _attrdef = dict(
        part_location_id=ElementBase.addAttr(notnone=True),
        order_id=ElementBase.addAttr(),
        desc=ElementBase.addAttr(default='', notnone=True),
        created_at=ElementBase.addAttr(type=int),
        amount=ElementBase.addAttr(type=int, default=1, notnone=True),
        price=ElementBase.addAttr(type=float, default=0.0, notnone=True)
    )

    def validate(self):
        errors = dict()
        if not docDB.exists('PartLocation', self['part_location_id']):
            errors['part_location_id'] = f"There is no PartLocation with id '{self['part_location_id']}'"
        if self['order_id'] is not None and not docDB.exists('Order', self['order_id']):
            errors['order_id'] = f"There is no Order with id '{self['order_id']}'"
        elif (self['order_id'] is not None and
                'part_location_id' not in errors and
                not docDB.get('Order', self['order_id'])['part_id'] == docDB.get('PartLocation', self['part_location_id'])['part_id']):
            errors['order_id'] = "Part of Order doesn't match Part of PartLocation"
        if self['amount'] == 0:
            errors['amount'] = "Can't be zero"
        elif self['order_id'] is not None and self['amount'] < 0:
            errors['amount'] = "Can't be negative"
        if self['order_id'] is None and self['price'] < 0:
            errors['price'] = "Can't be negative"
        if self['created_at'] is not None and self['created_at'] < 0:
            errors['created_at'] = "Can't be negative"
        if self['order_id'] is not None and 'order_id' not in errors:
            saved_amount = docDB.sum(self.__class__.__name__, 'amount', {'order_id': self['order_id'], '_id': {'$ne': self['_id']}})
            if docDB.get('Order', self['order_id'])['amount'] < saved_amount + self['amount']:
                errors['amount'] = 'Would exceed amount of Order'
        if (self['amount'] < 0 and
                docDB.sum(self.__class__.__name__, 'amount', {'part_location_id': self['part_location_id'], '_id': {'$ne': self['_id']}}) + self['amount'] < 0):
            errors['amount'] = 'Results in negative PartLocation stock_level'
        return errors

    def save_pre(self):
        if self['created_at'] is None:
            self['created_at'] = int(time.time())
        if self['order_id'] is not None:
            from elements import Order
            o = Order.get(self['order_id'])
            self['price'] = float(Decimal(o['price']) / o['amount'] * self['amount'])
