import unittest
from helpers.docdb import docDB
from elements import Part, Unit, Category, Footprint, MountingStyle, Distributor, PartDistributor, Order, StorageLocation, PartLocation, StockChange
from testcases._wrapper import ApiTestBase, setUpModule, tearDownModule


class TestPart(unittest.TestCase):
    def setUp(self):
        docDB.clear()
        c1 = Category({'name': 'cat1'})
        c1.save()
        self.c1 = c1['_id']
        u1 = Unit({'name': 'unit1'})
        u1.save()
        self.u1 = u1['_id']
        ms1 = MountingStyle({'name': 'ms1'})
        ms1.save()
        self.ms1 = ms1['_id']
        ms2 = MountingStyle({'name': 'ms2'})
        ms2.save()
        self.ms2 = ms2['_id']
        fp1 = Footprint({'name': 'fp1', 'mounting_style_id': ms1['_id']})
        fp1.save()
        self.fp1 = fp1['_id']

    def test_name_notnone(self):
        self.assertEqual(len(Part.all()), 0)
        # if name is None it can't be saved
        p1 = Part({'unit_id': self.u1, 'category_id': self.c1, 'name': None})
        result = p1.save()
        self.assertIn('name', result['errors'])
        self.assertEqual(len(Part.all()), 0)
        # now with valid name
        p1['name'] = 'somename'
        result = p1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Part.all()), 1)
        # duplicates are ok
        p2 = Part({'unit_id': self.u1, 'category_id': self.c1, 'name': 'somename'})
        result = p2.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Part.all()), 2)

    def test_unit_id_FK_and_notnone(self):
        self.assertEqual(len(Part.all()), 0)
        # if unit_id is None it can't be saved
        p1 = Part({'name': 'somepart', 'category_id': self.c1, 'unit_id': None})
        result = p1.save()
        self.assertIn('unit_id', result['errors'])
        self.assertEqual(len(Part.all()), 0)
        # if unit_id is not a valid id it can't be saved
        p1['unit_id'] = 'somerandomstring'
        result = p1.save()
        self.assertIn('unit_id', result['errors'])
        self.assertEqual(len(Part.all()), 0)
        # now with valid id it is possible to save
        p1['unit_id'] = self.u1
        result = p1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Part.all()), 1)

    def test_footprint_id_FK_or_None(self):
        self.assertEqual(len(Part.all()), 0)
        # if footprint_id is None it can be saved
        p1 = Part({'name': 'somepart', 'category_id': self.c1, 'unit_id': self.u1, 'footprint_id': None})
        result = p1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Part.all()), 1)
        # if footprint_id is not a valid id it can't be saved
        p2 = Part({'name': 'somepart', 'category_id': self.c1, 'unit_id': self.u1, 'footprint_id': 'somerandomstring'})
        result = p2.save()
        self.assertIn('footprint_id', result['errors'])
        self.assertEqual(len(Part.all()), 1)
        # now with valid id it is possible to save
        p2['footprint_id'] = self.fp1
        result = p2.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Part.all()), 2)

    def test_mounting_style_id_FK_or_None(self):
        self.assertEqual(len(Part.all()), 0)
        # if mounting_style_id is None it can be saved
        p1 = Part({'name': 'somepart', 'category_id': self.c1, 'unit_id': self.u1, 'mounting_style_id': None})
        result = p1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Part.all()), 1)
        # if mounting_style_id is not a valid id it can't be saved
        p2 = Part({'name': 'somepart', 'category_id': self.c1, 'unit_id': self.u1, 'mounting_style_id': 'somerandomstring'})
        result = p2.save()
        self.assertIn('mounting_style_id', result['errors'])
        self.assertEqual(len(Part.all()), 1)
        # now with valid id it is possible to save
        p2['mounting_style_id'] = self.ms1
        result = p2.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Part.all()), 2)

    def test_category_id_FK_and_notnone(self):
        self.assertEqual(len(Part.all()), 0)
        # if category_id is None it can't be saved
        p1 = Part({'name': 'somepart', 'unit_id': self.u1, 'category_id': None})
        result = p1.save()
        self.assertIn('category_id', result['errors'])
        self.assertEqual(len(Part.all()), 0)
        # if category_id is not a valid id it can't be saved
        p1['category_id'] = 'somerandomid'
        result = p1.save()
        self.assertIn('category_id', result['errors'])
        self.assertEqual(len(Part.all()), 0)
        # now with valid id it is possible to save
        p1['category_id'] = self.c1
        result = p1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Part.all()), 1)

    def test_footprint_overwrites_mounting_style(self):
        fp1 = Footprint.get(self.fp1)
        fp1['mounting_style_id'] = self.ms1
        fp1.save()
        ms2 = MountingStyle({'name': 'secondms'})
        ms2.save()
        p = Part({'name': 'somepart', 'category_id': self.c1, 'unit_id': self.u1, 'footprint_id': fp1['_id'], 'mounting_style_id': ms2['_id']})
        p.save()
        self.assertEqual(len(Part.all()), 1)
        p.reload()
        self.assertNotEqual(p['mounting_style_id'], ms2['_id'])
        self.assertEqual(p['mounting_style_id'], self.ms1)

    def test_open_orders(self):
        p = Part({'unit_id': self.u1, 'category_id': self.c1, 'name': 'somename1'})
        p.save()
        sl = StorageLocation({'name': 'sl1'})
        sl.save()
        pl = PartLocation({'part_id': p['_id'], 'storage_location_id': sl['_id']})
        pl.save()
        # no Order = no open_orders
        self.assertFalse(p.open_orders())
        # add two Order that are not completed restults in open_orders
        o1 = Order({'part_id': p['_id'], 'amount': 10})
        o1.save()
        o2 = Order({'part_id': p['_id'], 'amount': 10})
        o2.save()
        p.drop_cache()
        self.assertFalse(o1.completed())
        self.assertFalse(o2.completed())
        self.assertTrue(p.open_orders())
        # complete one Order still one open
        sc = StockChange({'part_location_id': pl['_id'], 'order_id': o1['_id'], 'amount': 10})
        sc.save()
        p.drop_cache()
        self.assertTrue(o1.completed())
        self.assertFalse(o2.completed())
        self.assertTrue(p.open_orders())
        # complete second Order none remains uncompleted
        sc = StockChange({'part_location_id': pl['_id'], 'order_id': o2['_id'], 'amount': 10})
        sc.save()
        p.drop_cache()
        self.assertTrue(o1.completed())
        self.assertTrue(o2.completed())
        self.assertFalse(p.open_orders())

    def test_stock_level(self):
        p = Part({'unit_id': self.u1, 'category_id': self.c1, 'name': 'somename1'})
        p.save()
        sl1 = StorageLocation({'name': 'sl1'})
        sl1.save()
        sl2 = StorageLocation({'name': 'sl2'})
        sl2.save()
        pl1 = PartLocation({'part_id': p['_id'], 'storage_location_id': sl1['_id']})
        pl1.save()
        pl2 = PartLocation({'part_id': p['_id'], 'storage_location_id': sl2['_id']})
        pl2.save()
        pl3 = PartLocation({'part_id': p['_id'], 'storage_location_id': sl1['_id']})
        pl3.save()
        # all stock_levels are 0
        for obj, val in zip([pl1, pl2, pl3, p], [0, 0, 0, 0]):
            obj.drop_cache()
            self.assertEqual(obj.stock_level(), val)
        # adding stock to first pl
        sc = StockChange({'part_location_id': pl1['_id'], 'amount': 5})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [5, 0, 0, 5]):
            obj.drop_cache()
            self.assertEqual(obj.stock_level(), val)
        # adding stock to second pl
        sc = StockChange({'part_location_id': pl2['_id'], 'amount': 6})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [5, 6, 0, 11]):
            obj.drop_cache()
            self.assertEqual(obj.stock_level(), val)
        # adding stock to third pl
        sc = StockChange({'part_location_id': pl3['_id'], 'amount': 7})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [5, 6, 7, 18]):
            obj.drop_cache()
            self.assertEqual(obj.stock_level(), val)
        # removing stock form first pl
        sc = StockChange({'part_location_id': pl1['_id'], 'amount': -4})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [1, 6, 7, 14]):
            obj.drop_cache()
            self.assertEqual(obj.stock_level(), val)
        # removing stock form second pl
        sc = StockChange({'part_location_id': pl2['_id'], 'amount': -3})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [1, 3, 7, 11]):
            obj.drop_cache()
            self.assertEqual(obj.stock_level(), val)
        # removing stock form third pl
        sc = StockChange({'part_location_id': pl3['_id'], 'amount': -2})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [1, 3, 5, 9]):
            obj.drop_cache()
            self.assertEqual(obj.stock_level(), val)
        # adding some stock back to second pl
        sc = StockChange({'part_location_id': pl2['_id'], 'amount': 4})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [1, 7, 5, 13]):
            obj.drop_cache()
            self.assertEqual(obj.stock_level(), val)
        # removing all stock form first pl
        sc = StockChange({'part_location_id': pl1['_id'], 'amount': -1})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [0, 7, 5, 12]):
            obj.drop_cache()
            self.assertEqual(obj.stock_level(), val)
        # removing all stock form second pl
        sc = StockChange({'part_location_id': pl2['_id'], 'amount': -7})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [0, 0, 5, 5]):
            obj.drop_cache()
            self.assertEqual(obj.stock_level(), val)
        # removing all stock form third pl
        sc = StockChange({'part_location_id': pl3['_id'], 'amount': -5})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [0, 0, 0, 0]):
            obj.drop_cache()
            self.assertEqual(obj.stock_level(), val)

    def test_stock_price(self):
        p = Part({'unit_id': self.u1, 'category_id': self.c1, 'name': 'somename1'})
        p.save()
        sl1 = StorageLocation({'name': 'sl1'})
        sl1.save()
        sl2 = StorageLocation({'name': 'sl2'})
        sl2.save()
        pl1 = PartLocation({'part_id': p['_id'], 'storage_location_id': sl1['_id']})
        pl1.save()
        pl2 = PartLocation({'part_id': p['_id'], 'storage_location_id': sl2['_id']})
        pl2.save()
        pl3 = PartLocation({'part_id': p['_id'], 'storage_location_id': sl1['_id']})
        pl3.save()
        # all stock_prices are 0
        for obj, val in zip([pl1, pl2, pl3, p], [0.0, 0.0, 0.0, 0.0]):
            obj.drop_cache()
            self.assertEqual(obj.stock_price(), val)
        # adding stock to first pl
        sc = StockChange({'part_location_id': pl1['_id'], 'amount': 5, 'price': 0.5})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [0.5, 0.0, 0.0, 0.5]):
            obj.drop_cache()
            self.assertEqual(obj.stock_price(), val)
        # adding stock to second pl
        sc = StockChange({'part_location_id': pl2['_id'], 'amount': 6, 'price': 1.2})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [0.5, 1.2, 0.0, 1.7]):
            obj.drop_cache()
            self.assertEqual(obj.stock_price(), val)
        # adding stock to third pl
        sc = StockChange({'part_location_id': pl3['_id'], 'amount': 7, 'price': 2.1})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [0.5, 1.2, 2.1, 3.8]):
            obj.drop_cache()
            self.assertEqual(obj.stock_price(), val)
        # removing stock form first pl
        sc = StockChange({'part_location_id': pl1['_id'], 'amount': -4})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [0.1, 1.2, 2.1, 3.4]):
            obj.drop_cache()
            self.assertEqual(obj.stock_price(), val)
        # removing stock form second pl
        sc = StockChange({'part_location_id': pl2['_id'], 'amount': -3})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [0.1, 0.6, 2.1, 2.8]):
            obj.drop_cache()
            self.assertEqual(obj.stock_price(), val)
        # removing stock form third pl
        sc = StockChange({'part_location_id': pl3['_id'], 'amount': -2})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [0.1, 0.6, 1.5, 2.2]):
            obj.drop_cache()
            self.assertEqual(obj.stock_price(), val)
        # adding some stock back to second pl
        sc = StockChange({'part_location_id': pl2['_id'], 'amount': 4, 'price': 1.6})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [0.1, 2.2, 1.5, 3.8]):
            obj.drop_cache()
            self.assertEqual(obj.stock_price(), val)
        # removing all stock form first pl
        sc = StockChange({'part_location_id': pl1['_id'], 'amount': -1})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [0.0, 2.2, 1.5, 3.7]):
            obj.drop_cache()
            self.assertEqual(obj.stock_price(), val)
        # removing all stock form second pl
        sc = StockChange({'part_location_id': pl2['_id'], 'amount': -7})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [0.0, 0.0, 1.5, 1.5]):
            obj.drop_cache()
            self.assertEqual(obj.stock_price(), val)
        # removing all stock form third pl
        sc = StockChange({'part_location_id': pl3['_id'], 'amount': -5})
        sc.save()
        for obj, val in zip([pl1, pl2, pl3, p], [0.0, 0.0, 0.0, 0.0]):
            obj.drop_cache()
            self.assertEqual(obj.stock_price(), val)

    def test_deletion(self):
        p1 = Part({'unit_id': self.u1, 'category_id': self.c1, 'name': 'somename1'})
        p1.save()
        p2 = Part({'unit_id': self.u1, 'category_id': self.c1, 'name': 'somename1'})
        p2.save()
        self.assertEqual(len(Part.all()), 2)
        p1.delete()
        self.assertEqual(len(Part.all()), 1)
        p2.delete()
        self.assertEqual(len(Part.all()), 0)

    def test_deletion_with_associated_partdistributor(self):
        # if Part is deleted all referred PartDistributor should also be deleted
        d = Distributor({'name': 'd1'})
        d.save()
        p1 = Part({'unit_id': self.u1, 'category_id': self.c1, 'name': 'somename1'})
        p1.save()
        p2 = Part({'unit_id': self.u1, 'category_id': self.c1, 'name': 'somename1'})
        p2.save()
        pd1 = PartDistributor({'distributor_id': d['_id'], 'part_id': p1['_id']})
        pd1.save()
        pd2 = PartDistributor({'distributor_id': d['_id'], 'part_id': p2['_id']})
        pd2.save()
        self.assertEqual(len(Part.all()), 2)
        self.assertEqual(len(PartDistributor.all()), 2)
        p1.delete()
        self.assertEqual(len(Part.all()), 1)
        self.assertEqual(len(PartDistributor.all()), 1)
        p2.delete()
        self.assertEqual(len(Part.all()), 0)
        self.assertEqual(len(PartDistributor.all()), 0)

    def test_deletion_with_associated_order(self):
        # if Part is deleted all referred Order should also be deleted
        d = Distributor({'name': 'd1'})
        d.save()
        p1 = Part({'unit_id': self.u1, 'category_id': self.c1, 'name': 'somename1'})
        p1.save()
        p2 = Part({'unit_id': self.u1, 'category_id': self.c1, 'name': 'somename1'})
        p2.save()
        o1 = Order({'distributor_id': d['_id'], 'part_id': p1['_id']})
        o1.save()
        o2 = Order({'distributor_id': d['_id'], 'part_id': p2['_id']})
        o2.save()
        self.assertEqual(len(Part.all()), 2)
        self.assertEqual(len(Order.all()), 2)
        p1.delete()
        self.assertEqual(len(Part.all()), 1)
        self.assertEqual(len(Order.all()), 1)
        p2.delete()
        self.assertEqual(len(Part.all()), 0)
        self.assertEqual(len(Order.all()), 0)

    def test_deletion_with_associated_partlocation(self):
        # if Part is deleted all referred PartLocation should also be deleted
        p1 = Part({'unit_id': self.u1, 'category_id': self.c1, 'name': 'somename1'})
        p1.save()
        p2 = Part({'unit_id': self.u1, 'category_id': self.c1, 'name': 'somename1'})
        p2.save()
        sl = StorageLocation({'name': 'Name1'})
        sl.save()
        pl1 = PartLocation({'storage_location_id': sl['_id'], 'part_id': p1['_id']})
        pl1.save()
        pl2 = PartLocation({'storage_location_id': sl['_id'], 'part_id': p2['_id']})
        pl2.save()
        self.assertEqual(len(Part.all()), 2)
        self.assertEqual(len(PartLocation.all()), 2)
        p1.delete()
        self.assertEqual(len(Part.all()), 1)
        self.assertEqual(len(PartLocation.all()), 1)
        p2.delete()
        self.assertEqual(len(Part.all()), 0)
        self.assertEqual(len(PartLocation.all()), 0)


setup_module = setUpModule
teardown_module = tearDownModule


class TestPartApi(ApiTestBase):
    _element = Part
    _path = 'part'
    _patch_valid = {'external_number': '1234'}
    _patch_invalid = {'footprint_id': 'invalidfootprint'}

    def setUp(self):
        docDB.clear()
        c1 = Category({'name': 'cat1'})
        c1.save()
        u1 = Unit({'name': 'unit1'})
        u1.save()
        self._setup_el1 = {'name': 'part1', 'unit_id': u1['_id'], 'category_id': c1['_id']}
        self._setup_el2 = {'name': 'part2', 'unit_id': u1['_id'], 'category_id': c1['_id']}
        self._post_valid = {'name': 'part3', 'unit_id': u1['_id'], 'category_id': c1['_id']}
        el = self._element(self._setup_el1)
        self.id1 = el.save().get('created')
        el = self._element(self._setup_el2)
        self.id2 = el.save().get('created')

    def test_calculated_attr_are_exposed(self):
        p = Part().get(self.id1)
        self.assertIsNotNone(p['_id'])
        self.assertNotIn('stock_level', p._attr)
        self.assertNotIn('stock_price', p._attr)
        self.assertNotIn('open_orders', p._attr)
        result = self.webapp_request(path=f'/{self._path}/{self.id1}/', method='GET')
        self.assertIn('stock_level', result.json)
        self.assertIn('stock_price', result.json)
        self.assertIn('open_orders', result.json)
