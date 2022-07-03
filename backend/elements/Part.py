from elements._elementBase import ElementBase, docDB
from decimal import Decimal
from elements import Footprint


class Part(ElementBase):
    _attrdef = dict(
        name=ElementBase.addAttr(notnone=True),
        desc=ElementBase.addAttr(default='', notnone=True),
        unit_id=ElementBase.addAttr(notnone=True),
        footprint_id=ElementBase.addAttr(),
        mounting_style_id=ElementBase.addAttr(),
        category_id=ElementBase.addAttr(notnone=True),
        external_number=ElementBase.addAttr(default='', notnone=True)
    )

    def validate(self):
        errors = dict()
        if not docDB.exists('Unit', self['unit_id']):
            errors['unit_id'] = f"There is no Unit with id '{self['unit_id']}'"
        if not docDB.exists('Category', self['category_id']):
            errors['category_id'] = f"There is no Category with id '{self['category_id']}'"
        if self['mounting_style_id'] is not None and not docDB.exists('MountingStyle', self['mounting_style_id']):
            errors['mounting_style_id'] = f"There is no MountingStyle with id '{self['mounting_style_id']}'"
        if self['footprint_id'] is not None and not docDB.exists('Footprint', self['footprint_id']):
            errors['footprint_id'] = f"There is no Footprint with id '{self['footprint_id']}'"
        return errors

    def save_pre(self):
        if self['footprint_id'] is not None:
            fp = Footprint.get(self['footprint_id'])
            self['mounting_style_id'] = fp['mounting_style_id']

    def delete_pre(self):
        from elements import PartDistributor, Order
        for pd in docDB.search_many('PartDistributor', {'part_id': self['_id']}):
            pd = PartDistributor(pd)
            pd.delete()
        for order in docDB.search_many('Order', {'part_id': self['_id']}):
            order = Order(order)
            order.delete()

    def stock_level(self):
        return 0

    def avg_price(self):
        return Decimal(0.00)

    def open_orders(self):
        return False

    def json(self):
        result = super().json()
        result['stock_level'] = self.stock_level()
        result['avg_price'] = float(self.avg_price())
        result['open_orders'] = self.open_orders()
        return result
