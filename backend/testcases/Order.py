import unittest
from helpers.docdb import docDB
from elements import Order, Unit, Category, Part, Distributor, StockChange, StorageLocation, PartLocation
from testcases._wrapper import ApiTestBase, setUpModule, tearDownModule


class TestOrder(unittest.TestCase):
    def setUp(self):
        docDB.clear()
        u = Unit({'name': 'u'})
        u.save()
        c = Category({'name': 'c'})
        c.save()
        p = Part({'name': 'p', 'unit_id': u['_id'], 'category_id': c['_id']})
        self.pid = p.save().get('created')
        d = Distributor({'name': 'd1'})
        self.did = d.save().get('created')

    def test_part_id_FK_and_notnone(self):
        self.assertEqual(len(Order.all()), 0)
        # if part_id is None it can't be saved
        el1 = Order({'distributor_id': self.did, 'part_id': None})
        result = el1.save()
        self.assertIn('not to be None', result['errors']['part_id'])
        self.assertEqual(len(Order.all()), 0)
        # if part_id is not a valid id it can't be saved
        el1['part_id'] = 'somerandomstring'
        result = el1.save()
        self.assertIn('part_id', result['errors'])
        self.assertEqual(len(Order.all()), 0)
        # now with valid id it is possible to save
        el1['part_id'] = self.pid
        result = el1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Order.all()), 1)

    def test_distributor_id_FK_or_None(self):
        self.assertEqual(len(Order.all()), 0)
        # None is a valid input
        element = Order({'part_id': self.pid, 'distributor_id': None})
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Order.all()), 1)
        # if distributor_id is not a valid id it can't be saved
        element = Order({'part_id': self.pid, 'distributor_id': 'somerandomstring'})
        result = element.save()
        self.assertIn('distributor_id', result['errors'])
        self.assertEqual(len(Order.all()), 1)
        # now with valid id it is possible to save
        element['distributor_id'] = self.did
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Order.all()), 2)

    def test_created_at_integer_or_None(self):
        self.assertEqual(len(Order.all()), 0)
        # int
        element = Order({'part_id': self.pid, 'distributor_id': self.did, 'created_at': '1'})
        result = element.save()
        self.assertIn('type', result['errors']['created_at'])
        self.assertEqual(len(Order.all()), 0)
        # None results in current TS
        element['created_at'] = None
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertIsNotNone(element['created_at'])
        self.assertEqual(len(Order.all()), 1)
        # negative not allowed
        element = Order({'part_id': self.pid, 'distributor_id': self.did, 'created_at': -1})
        result = element.save()
        self.assertIn('negative', result['errors']['created_at'])
        self.assertEqual(len(Order.all()), 1)
        # working
        element['created_at'] = 1
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Order.all()), 2)

    def test_amount_integer_and_notnone_and_positive(self):
        self.assertEqual(len(Order.all()), 0)
        # notnone
        element = Order({'part_id': self.pid, 'distributor_id': self.did, 'amount': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['amount'])
        self.assertEqual(len(Order.all()), 0)
        # int
        element = Order({'part_id': self.pid, 'distributor_id': self.did, 'amount': '1'})
        result = element.save()
        self.assertIn('type', result['errors']['amount'])
        self.assertEqual(len(Order.all()), 0)
        # zero not allowed
        element = Order({'part_id': self.pid, 'distributor_id': self.did, 'amount': 0})
        result = element.save()
        self.assertIn('one or more', result['errors']['amount'])
        self.assertEqual(len(Order.all()), 0)
        # negative not allowed
        element = Order({'part_id': self.pid, 'distributor_id': self.did, 'amount': -1})
        result = element.save()
        self.assertIn('one or more', result['errors']['amount'])
        self.assertEqual(len(Order.all()), 0)
        # working
        element['amount'] = 1
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Order.all()), 1)

    def test_price_float_and_notnone_and_positive(self):
        self.assertEqual(len(Order.all()), 0)
        # notnone
        element = Order({'part_id': self.pid, 'distributor_id': self.did, 'price': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['price'])
        self.assertEqual(len(Order.all()), 0)
        # float
        element = Order({'part_id': self.pid, 'distributor_id': self.did, 'price': '1.23'})
        result = element.save()
        self.assertIn('type', result['errors']['price'])
        self.assertEqual(len(Order.all()), 0)
        # negative not allowed
        element = Order({'part_id': self.pid, 'distributor_id': self.did, 'price': -0.5})
        result = element.save()
        self.assertIn('negative', result['errors']['price'])
        self.assertEqual(len(Order.all()), 0)
        # working
        element['price'] = 1.0
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Order.all()), 1)

    def test_completed(self):
        o1 = Order({'part_id': self.pid, 'distributor_id': self.did, 'amount': 10})
        o1.save()
        o2 = Order({'part_id': self.pid, 'distributor_id': self.did, 'amount': 10})
        o2.save()
        sl = StorageLocation({'name': 'sl1'})
        sl.save()
        pl = PartLocation({'part_id': self.pid, 'storage_location_id': sl['_id']})
        pl.save()
        self.assertFalse(o1.completed())
        self.assertFalse(o2.completed())
        # completing Order in one go
        sc = StockChange({'part_location_id': pl['_id'], 'order_id': o1['_id'], 'amount': 10})
        sc.save()
        self.assertTrue(o1.completed())
        self.assertFalse(o2.completed())
        # partially complete Order
        sc = StockChange({'part_location_id': pl['_id'], 'order_id': o2['_id'], 'amount': 6})
        sc.save()
        self.assertTrue(o1.completed())
        self.assertFalse(o2.completed())
        # completing Order
        sc = StockChange({'part_location_id': pl['_id'], 'order_id': o2['_id'], 'amount': 4})
        sc.save()
        self.assertTrue(o1.completed())
        self.assertTrue(o2.completed())

    def test_deletion(self):
        el1 = Order({'part_id': self.pid, 'distributor_id': self.did})
        el1.save()
        el2 = Order({'part_id': self.pid, 'distributor_id': self.did})
        el2.save()
        self.assertEqual(len(Order.all()), 2)
        el1.delete()
        self.assertEqual(len(Order.all()), 1)
        el2.delete()
        self.assertEqual(len(Order.all()), 0)

    def test_deletion_with_associated_stock_change(self):
        # if Order is deleted assiciated StockChange gets None'ed on order_id
        sl = StorageLocation({'name': 'sl1'})
        sl.save()
        pl = PartLocation({'part_id': self.pid, 'storage_location_id': sl['_id']})
        pl.save()
        o1 = Order({'part_id': self.pid, 'distributor_id': self.did, 'amount': 10})
        o1.save()
        o2 = Order({'part_id': self.pid, 'distributor_id': self.did, 'amount': 10})
        o2.save()
        sc1 = StockChange({'part_location_id': pl['_id'], 'order_id': o1['_id']})
        sc1.save()
        sc2 = StockChange({'part_location_id': pl['_id'], 'order_id': o2['_id']})
        sc2.save()
        sc3 = StockChange({'part_location_id': pl['_id'], 'order_id': o2['_id']})
        sc3.save()
        self.assertIsNotNone(sc1['order_id'])
        self.assertIsNotNone(sc2['order_id'])
        self.assertIsNotNone(sc3['order_id'])
        o1.delete()
        sc1.reload()
        sc2.reload()
        sc3.reload()
        self.assertIsNone(sc1['order_id'])
        self.assertIsNotNone(sc2['order_id'])
        self.assertIsNotNone(sc3['order_id'])
        o2.delete()
        sc1.reload()
        sc2.reload()
        sc3.reload()
        self.assertIsNone(sc1['order_id'])
        self.assertIsNone(sc2['order_id'])
        self.assertIsNone(sc3['order_id'])


setup_module = setUpModule
teardown_module = tearDownModule


class TestOrderApi(ApiTestBase):
    _element = Order
    _path = 'order'
    _patch_valid = {'amount': 2}
    _patch_invalid = {'amount': -1}

    def setUp(self):
        docDB.clear()
        u = Unit({'name': 'u'})
        u.save()
        c = Category({'name': 'c'})
        c.save()
        p = Part({'name': 'p', 'unit_id': u['_id'], 'category_id': c['_id']})
        p.save()
        d = Distributor({'name': 'd1'})
        d.save()
        self._setup_el1 = {'part_id': p['_id'], 'distributor_id': d['_id']}
        self._setup_el2 = {'part_id': p['_id'], 'distributor_id': d['_id']}
        self._post_valid = {'part_id': p['_id'], 'distributor_id': d['_id']}
        el = self._element(self._setup_el1)
        self.id1 = el.save().get('created')
        el = self._element(self._setup_el2)
        self.id2 = el.save().get('created')

    def test_calculated_attr_are_exposed(self):
        o = Order().get(self.id1)
        self.assertIsNotNone(o['_id'])
        self.assertNotIn('completed', o._attr)
        result = self.webapp_request(path=f'/{self._path}/{self.id1}/', method='GET')
        self.assertIn('completed', result.json)
