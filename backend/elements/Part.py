from elements._elementBase import ElementBase
from decimal import Decimal


class Part(ElementBase):
    _attrdef = dict(
        name=ElementBase.addAttr(notnone=True),
        desc=ElementBase.addAttr(default=''),
        unit_id=ElementBase.addAttr(notnone=True),
        footprint_id=ElementBase.addAttr(),
        mounting_style_id=ElementBase.addAttr(),
        category_id=ElementBase.addAttr(notnone=True),
        external_number=ElementBase.addAttr(default='')
    )

    def stock_level(self):
        return 0

    def avg_price(self):
        return Decimal(0.00)

    def open_orders(self):
        return False
