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

    def delete_pre(self):
        from elements import StockChange
        for sc in docDB.search_many('StockChange', {'part_location_id': self['_id']}):
            sc = StockChange(sc)
            sc.delete()

    def delete_post(self):
        if docDB.search_one(self.__class__.__name__, {'default': True}) is None:
            somepl = docDB.search_one(self.__class__.__name__, {})
            if somepl is not None:
                somepl = PartLocation(somepl)
                somepl['default'] = True
                somepl.save()

    def stock_level(self):
        if 'stock_level' in self._cache:
            return self._cache['stock_level']
        result = docDB.sum('StockChange', 'amount', {'part_location_id': self['_id']})
        self._cache['stock_level'] = result
        return result

    def stock_price(self):
        if 'stock_price' in self._cache:
            return self._cache['stock_price']
        from decimal import Decimal
        result = Decimal('0.0')
        removed = docDB.sum('StockChange', 'amount', {'part_location_id': self['_id'], 'amount': {'$lt': 0}}) * -1
        for sc in docDB.search_many('StockChange', {'part_location_id': self['_id'], 'amount': {'$gt': 0}}):
            if removed == 0:
                result += Decimal(str(sc['price']))
            elif removed >= sc['amount']:
                removed -= sc['amount']
            else:
                result += Decimal(str(sc['price'])) / sc['amount'] * (sc['amount'] - removed)
                removed = 0
        self._cache['stock_price'] = float(result)
        return float(result)

    def json(self):
        result = super().json()
        result['stock_level'] = self.stock_level()
        result['stock_price'] = self.stock_price()
        return result
