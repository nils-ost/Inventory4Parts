import unittest
from helpers.docdb import docDB
from elements import PartLocation, Unit, Category, Part, StorageLocation, StockChange
from testcases._wrapper import ApiTestBase, setUpModule, tearDownModule


class TestPartLocation(unittest.TestCase):
    def setUp(self):
        docDB.clear()
        u = Unit({'name': 'u'})
        u.save()
        c = Category({'name': 'c'})
        c.save()
        p = Part({'name': 'p', 'unit_id': u['_id'], 'category_id': c['_id']})
        self.pid = p.save().get('created')
        sl = StorageLocation({'name': 'sl1'})
        self.slid = sl.save().get('created')

    def test_part_id_FK_and_notnone(self):
        self.assertEqual(len(PartLocation.all()), 0)
        # if part_id is None it can't be saved
        el1 = PartLocation({'storage_location_id': self.slid, 'part_id': None})
        result = el1.save()
        self.assertIn('not to be None', result['errors']['part_id'])
        self.assertEqual(len(PartLocation.all()), 0)
        # if part_id is not a valid id it can't be saved
        el1['part_id'] = 'somerandomstring'
        result = el1.save()
        self.assertIn('part_id', result['errors'])
        self.assertEqual(len(PartLocation.all()), 0)
        # now with valid id it is possible to save
        el1['part_id'] = self.pid
        result = el1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(PartLocation.all()), 1)

    def test_storage_location_id_FK_and_notnone(self):
        self.assertEqual(len(PartLocation.all()), 0)
        # if storage_location_id is None it can't be saved
        el1 = PartLocation({'part_id': self.pid, 'storage_location_id': None})
        result = el1.save()
        self.assertIn('not to be None', result['errors']['storage_location_id'])
        self.assertEqual(len(PartLocation.all()), 0)
        # if storage_location_id is not a valid id it can't be saved
        el1['storage_location_id'] = 'somerandomstring'
        result = el1.save()
        self.assertIn('storage_location_id', result['errors'])
        self.assertEqual(len(PartLocation.all()), 0)
        # now with valid id it is possible to save
        el1['storage_location_id'] = self.slid
        result = el1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(PartLocation.all()), 1)

    def test_desc_notnone(self):
        self.assertEqual(len(PartLocation.all()), 0)
        # notnone
        element = PartLocation({'part_id': self.pid, 'storage_location_id': self.slid, 'desc': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['desc'])
        self.assertEqual(len(PartLocation.all()), 0)
        # working
        element['desc'] = 'text'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(PartLocation.all()), 1)

    def test_default_bool_and_notnone(self):
        element = PartLocation({'part_id': self.pid, 'storage_location_id': self.slid})
        # notnone
        element['default'] = None
        result = element.save()
        self.assertIn('not to be None', result['errors']['default'])
        self.assertEqual(len(PartLocation.all()), 0)
        # other type than bool
        element['default'] = 'hi'
        result = element.save()
        self.assertIn('type', result['errors']['default'])
        self.assertEqual(len(PartLocation.all()), 0)
        # working
        element['default'] = True
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(PartLocation.all()), 1)

    def test_only_one_default_exists(self):
        # first one gets default
        el1 = PartLocation({'part_id': self.pid, 'storage_location_id': self.slid})
        self.assertFalse(el1['default'])
        el1.save()
        self.assertTrue(el1['default'])
        # new one is set to be default
        el2 = PartLocation({'part_id': self.pid, 'storage_location_id': self.slid, 'default': True})
        el2.save()
        el1.reload()
        self.assertFalse(el1['default'])
        self.assertTrue(el2['default'])
        # new one is not the new default, and does not change the default
        el3 = PartLocation({'part_id': self.pid, 'storage_location_id': self.slid})
        el3.save()
        el1.reload()
        el2.reload()
        self.assertFalse(el1['default'])
        self.assertTrue(el2['default'])
        self.assertFalse(el3['default'])

    def test_deletion_of_default(self):
        el1 = PartLocation({'part_id': self.pid, 'storage_location_id': self.slid})
        el1.save()
        el2 = PartLocation({'part_id': self.pid, 'storage_location_id': self.slid, 'default': True})
        el2.save()
        el3 = PartLocation({'part_id': self.pid, 'storage_location_id': self.slid})
        el3.save()
        el1.reload()
        el2.reload()
        el3.reload()
        self.assertFalse(el1['default'])
        self.assertTrue(el2['default'])
        self.assertFalse(el3['default'])
        # deleting non default, does not change the default
        el3.delete()
        el2.reload()
        el1.reload()
        self.assertFalse(el1['default'])
        self.assertTrue(el2['default'])
        # deleting default promotes a random one to be default
        el2.delete()
        el1.reload()
        self.assertTrue(el1['default'])
        # deleting last one does not produce an error
        result = el1.delete()
        self.assertNotIn('error', result)

    def test_stock_level(self):
        pl = PartLocation({'part_id': self.pid, 'storage_location_id': self.slid})
        pl.save()
        self.assertEqual(pl.stock_level(), 0)
        # Adding stock
        sc = StockChange({'part_location_id': pl['_id'], 'amount': 5})
        sc.save()
        self.assertEqual(pl.stock_level(), 5)
        # Adding more stock
        sc = StockChange({'part_location_id': pl['_id'], 'amount': 6})
        sc.save()
        self.assertEqual(pl.stock_level(), 11)
        # Removing stock
        sc = StockChange({'part_location_id': pl['_id'], 'amount': -9})
        sc.save()
        self.assertEqual(pl.stock_level(), 2)
        # Adding some stock
        sc = StockChange({'part_location_id': pl['_id'], 'amount': 2})
        sc.save()
        self.assertEqual(pl.stock_level(), 4)
        # Removing the rest stock
        sc = StockChange({'part_location_id': pl['_id'], 'amount': -4})
        sc.save()
        self.assertEqual(pl.stock_level(), 0)

    def test_deletion(self):
        el1 = PartLocation({'part_id': self.pid, 'storage_location_id': self.slid})
        el1.save()
        el2 = PartLocation({'part_id': self.pid, 'storage_location_id': self.slid})
        el2.save()
        self.assertEqual(len(PartLocation.all()), 2)
        el1.delete()
        self.assertEqual(len(PartLocation.all()), 1)
        el2.delete()
        self.assertEqual(len(PartLocation.all()), 0)

    def test_deletion_with_associated_stock_change(self):
        pass
        # if a PartLocation is deleted all associated StockChange are deleted as well
        pl1 = PartLocation({'part_id': self.pid, 'storage_location_id': self.slid})
        pl1.save()
        pl2 = PartLocation({'part_id': self.pid, 'storage_location_id': self.slid})
        pl2.save()
        sc1 = StockChange({'part_location_id': pl1['_id']})
        sc1.save()
        sc2 = StockChange({'part_location_id': pl2['_id']})
        sc2.save()
        sc3 = StockChange({'part_location_id': pl2['_id']})
        sc3.save()
        self.assertEqual(len(StockChange.all()), 3)
        pl1.delete()
        self.assertEqual(len(StockChange.all()), 2)
        pl2.delete()
        self.assertEqual(len(StockChange.all()), 0)


setup_module = setUpModule
teardown_module = tearDownModule


class TestPartLocationApi(ApiTestBase):
    _element = PartLocation
    _path = 'partlocation'
    _patch_valid = {'desc': 'some not'}
    _patch_invalid = {'desc': None}

    def setUp(self):
        docDB.clear()
        u = Unit({'name': 'u'})
        u.save()
        c = Category({'name': 'c'})
        c.save()
        p = Part({'name': 'p', 'unit_id': u['_id'], 'category_id': c['_id']})
        p.save()
        sl = StorageLocation({'name': 'd1'})
        sl.save()
        self._setup_el1 = {'part_id': p['_id'], 'storage_location_id': sl['_id']}
        self._setup_el2 = {'part_id': p['_id'], 'storage_location_id': sl['_id']}
        self._post_valid = {'part_id': p['_id'], 'storage_location_id': sl['_id']}
        el = self._element(self._setup_el1)
        self.id1 = el.save().get('created')
        el = self._element(self._setup_el2)
        self.id2 = el.save().get('created')

    def test_calculated_attr_are_exposed(self):
        pl = PartLocation().get(self.id1)
        self.assertIsNotNone(pl['_id'])
        self.assertNotIn('stock_level', pl._attr)
        self.assertNotIn('stock_price', pl._attr)
        result = self.webapp_request(path=f'/{self._path}/{self.id1}/', method='GET')
        self.assertIn('stock_level', result.json)
        self.assertIn('stock_price', result.json)
