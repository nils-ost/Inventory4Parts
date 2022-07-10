import unittest
from helpers.docdb import docDB
from elements import Order, Unit, Category, Part, PartLocation, StorageLocation, StockChange
from testcases._wrapper import ApiTestBase, setUpModule, tearDownModule


class TestStockChange(unittest.TestCase):
    def setUp(self):
        docDB.clear()
        u = Unit({'name': 'u'})
        u.save()
        c = Category({'name': 'c'})
        c.save()
        p1 = Part({'name': 'p', 'unit_id': u['_id'], 'category_id': c['_id']})
        p1.save()
        p2 = Part({'name': 'p2', 'unit_id': u['_id'], 'category_id': c['_id']})
        p2.save()
        sl = StorageLocation({'name': 'sl1'})
        sl.save()
        pl1 = PartLocation({'part_id': p1['_id'], 'storage_location_id': sl['_id']})
        self.pl1id = pl1.save().get('created')
        pl2 = PartLocation({'part_id': p2['_id'], 'storage_location_id': sl['_id']})
        self.pl2id = pl2.save().get('created')
        o1 = Order({'part_id': p1['_id'], 'amount': 10, 'price': 1.0})
        self.o1id = o1.save().get('created')
        o2 = Order({'part_id': p1['_id'], 'amount': 10, 'price': 2.0})
        self.o2id = o2.save().get('created')

    def test_part_location_id_FK_and_notnone(self):
        self.assertEqual(len(StockChange.all()), 0)
        # if part_location_id is None it can't be saved
        el1 = StockChange({'part_location_id': None})
        result = el1.save()
        self.assertIn('not to be None', result['errors']['part_location_id'])
        self.assertEqual(len(StockChange.all()), 0)
        # if part_location_id is not a valid id it can't be saved
        el1['part_location_id'] = 'somerandomstring'
        result = el1.save()
        self.assertIn('part_location_id', result['errors'])
        self.assertEqual(len(StockChange.all()), 0)
        # now with valid id it is possible to save
        el1['part_location_id'] = self.pl1id
        result = el1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StockChange.all()), 1)

    def test_order_id_FK_or_None(self):
        self.assertEqual(len(StockChange.all()), 0)
        # None is a valid input
        element = StockChange({'part_location_id': self.pl1id, 'order_id': None})
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StockChange.all()), 1)
        # if order_id is not a valid id it can't be saved
        element = StockChange({'part_location_id': self.pl2id, 'order_id': 'somerandomstring'})
        result = element.save()
        self.assertIn('order_id', result['errors'])
        self.assertEqual(len(StockChange.all()), 1)
        # if Part of Order and Part of PartLocation do not match StockChange can't be saved
        element['order_id'] = self.o1id
        result = element.save()
        self.assertIn('order_id', result['errors'])
        self.assertEqual(len(StockChange.all()), 1)
        # now with valid id and matching PartLocation it is possible to save
        element['order_id'] = self.o1id
        element['part_location_id'] = self.pl1id
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StockChange.all()), 2)

    def test_desc_notnone(self):
        self.assertEqual(len(StockChange.all()), 0)
        # notnone
        element = StockChange({'part_location_id': self.pl1id, 'desc': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['desc'])
        self.assertEqual(len(StockChange.all()), 0)
        # working
        element['desc'] = 'text'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StockChange.all()), 1)

    def test_created_at_integer_or_None(self):
        self.assertEqual(len(StockChange.all()), 0)
        # int
        element = StockChange({'part_location_id': self.pl1id, 'created_at': '1'})
        result = element.save()
        self.assertIn('type', result['errors']['created_at'])
        self.assertEqual(len(StockChange.all()), 0)
        # None results in current TS
        element['created_at'] = None
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertIsNotNone(element['created_at'])
        self.assertEqual(len(StockChange.all()), 1)
        # negative not allowed
        element = StockChange({'part_location_id': self.pl1id, 'created_at': -1})
        result = element.save()
        self.assertIn('negative', result['errors']['created_at'])
        self.assertEqual(len(StockChange.all()), 1)
        # working
        element['created_at'] = 1
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StockChange.all()), 2)

    def test_amount_integer_and_notnone_and_notzero(self):
        self.assertEqual(len(StockChange.all()), 0)
        # notnone
        element = StockChange({'part_location_id': self.pl1id, 'amount': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['amount'])
        self.assertEqual(len(StockChange.all()), 0)
        # int
        element['amount'] = '1'
        result = element.save()
        self.assertIn('type', result['errors']['amount'])
        self.assertEqual(len(StockChange.all()), 0)
        # zero not allowed
        element['amount'] = 0
        result = element.save()
        self.assertIn('zero', result['errors']['amount'])
        self.assertEqual(len(StockChange.all()), 0)
        # positive allowed
        element['amount'] = 1
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StockChange.all()), 1)
        # negative allowed
        element = StockChange({'part_location_id': self.pl1id, 'amount': -1})
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StockChange.all()), 2)

    def test_amount_with_order(self):
        self.assertEqual(len(StockChange.all()), 0)
        # amount can't be negative
        element = StockChange({'part_location_id': self.pl1id, 'order_id': self.o1id, 'amount': -1})
        result = element.save()
        self.assertIn('negative', result['errors']['amount'])
        self.assertEqual(len(StockChange.all()), 0)
        # amount can't exceed Order amount
        element['amount'] = 11
        result = element.save()
        self.assertIn('exceed', result['errors']['amount'])
        self.assertEqual(len(StockChange.all()), 0)
        # amount within Order amount is fine
        element['amount'] = 9
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StockChange.all()), 1)
        # multiple StockChange can't exceed Order amount
        element = StockChange({'part_location_id': self.pl1id, 'order_id': self.o1id, 'amount': 2})
        result = element.save()
        self.assertIn('exceed', result['errors']['amount'])
        self.assertEqual(len(StockChange.all()), 1)
        # multiple within Order amount is fine again
        element['amount'] = 1
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StockChange.all()), 2)

    def test_amount_with_part_location(self):
        # StockChange must not render PartLocation stock_level to be negative
        # try to remove stock from a zero PartLocation does not work
        element = StockChange({'part_location_id': self.pl1id, 'amount': -1})
        result = element.save()
        self.assertIn('negative PartLocation', result['errors']['amount'])
        # adding some stock does work
        element = StockChange({'part_location_id': self.pl1id, 'amount': 5})
        result = element.save()
        self.assertNotIn('errors', result)
        # removing stock within stock_level also works
        element = StockChange({'part_location_id': self.pl1id, 'amount': -4})
        result = element.save()
        self.assertNotIn('errors', result)
        # but removing mor than stock_level is capable of is not allowed again
        element = StockChange({'part_location_id': self.pl1id, 'amount': -2})
        result = element.save()
        self.assertIn('negative PartLocation', result['errors']['amount'])
        # removing up to stock_level zero is ok
        element = StockChange({'part_location_id': self.pl1id, 'amount': -1})
        result = element.save()
        self.assertNotIn('errors', result)
        # and again removing more is not ok
        element = StockChange({'part_location_id': self.pl1id, 'amount': -1})
        result = element.save()
        self.assertIn('negative PartLocation', result['errors']['amount'])

    def test_price_float_and_notnone_and_notnegative(self):
        self.assertEqual(len(StockChange.all()), 0)
        # notnone
        element = StockChange({'part_location_id': self.pl1id, 'price': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['price'])
        self.assertEqual(len(StockChange.all()), 0)
        # float
        element['price'] = '1.23'
        result = element.save()
        self.assertIn('type', result['errors']['price'])
        self.assertEqual(len(StockChange.all()), 0)
        # negative not allowed
        element['price'] = -0.5
        result = element.save()
        self.assertIn('negative', result['errors']['price'])
        self.assertEqual(len(StockChange.all()), 0)
        # zero allowed
        element['price'] = 0.0
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StockChange.all()), 1)
        # positive allowed
        element = StockChange({'part_location_id': self.pl1id, 'price': 1.0})
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StockChange.all()), 2)

    def test_price_with_order(self):
        # price is calculated based on Order price
        element = StockChange({'part_location_id': self.pl1id, 'order_id': self.o1id, 'amount': 2})
        element.save()
        self.assertEqual(element['price'], 0.2)
        # different Order different price
        element = StockChange({'part_location_id': self.pl1id, 'order_id': self.o2id, 'amount': 2})
        element.save()
        self.assertEqual(element['price'], 0.4)
        # manual inputs are overwritten
        element = StockChange({'part_location_id': self.pl1id, 'order_id': self.o1id, 'amount': 3, 'price': 1.0})
        element.save()
        self.assertEqual(element['price'], 0.3)
        # negative now doesn't matter
        element = StockChange({'part_location_id': self.pl1id, 'order_id': self.o2id, 'amount': 3, 'price': -1.0})
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(element['price'], 0.6)

    def test_deletion(self):
        el1 = StockChange({'part_location_id': self.pl1id})
        el1.save()
        el2 = StockChange({'part_location_id': self.pl1id})
        el2.save()
        self.assertEqual(len(StockChange.all()), 2)
        el1.delete()
        self.assertEqual(len(StockChange.all()), 1)
        el2.delete()
        self.assertEqual(len(StockChange.all()), 0)


setup_module = setUpModule
teardown_module = tearDownModule


class TestStockChangeApi(ApiTestBase):
    _element = StockChange
    _path = 'stockchange'
    _patch_valid = {'price': 2.0}
    _patch_invalid = {'price': -1.0}

    def setUp(self):
        docDB.clear()
        u = Unit({'name': 'u'})
        u.save()
        c = Category({'name': 'c'})
        c.save()
        p1 = Part({'name': 'p', 'unit_id': u['_id'], 'category_id': c['_id']})
        p1.save()
        p2 = Part({'name': 'p2', 'unit_id': u['_id'], 'category_id': c['_id']})
        p2.save()
        sl = StorageLocation({'name': 'sl1'})
        sl.save()
        pl1 = PartLocation({'part_id': p1['_id'], 'storage_location_id': sl['_id']})
        pl1.save()
        self._setup_el1 = {'part_location_id': pl1['_id'], 'amount': 1}
        self._setup_el2 = {'part_location_id': pl1['_id'], 'amount': 2}
        self._post_valid = {'part_location_id': pl1['_id'], 'amount': 3}
        el = self._element(self._setup_el1)
        self.id1 = el.save().get('created')
        el = self._element(self._setup_el2)
        self.id2 = el.save().get('created')
