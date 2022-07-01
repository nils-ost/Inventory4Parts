import unittest
from helpers.docdb import docDB
from elements import Unit, Category, Part, Distributor, PartDistributor
from testcases._wrapper import ApiTestBase, setUpModule, tearDownModule


class TestPartDistributor(unittest.TestCase):
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
        self.assertEqual(len(PartDistributor.all()), 0)
        # if part_id is None it can't be saved
        el1 = PartDistributor({'distributor_id': self.did, 'part_id': None})
        result = el1.save()
        self.assertIn('not to be None', result['errors']['part_id'])
        self.assertEqual(len(PartDistributor.all()), 0)
        # if part_id is not a valid id if can't be saved
        el1['part_id'] = 'somerandomstring'
        result = el1.save()
        self.assertIn('part_id', result['errors'])
        self.assertEqual(len(PartDistributor.all()), 0)
        # now with valid id it is possible to save
        el1['part_id'] = self.pid
        result = el1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(PartDistributor.all()), 1)

    def test_distributor_id_FK_and_notnone(self):
        self.assertEqual(len(PartDistributor.all()), 0)
        # if distributor_id is None it can't be saved
        el1 = PartDistributor({'part_id': self.pid, 'distributor_id': None})
        result = el1.save()
        self.assertIn('not to be None', result['errors']['distributor_id'])
        self.assertEqual(len(PartDistributor.all()), 0)
        # if distributor_id is not a valid id if can't be saved
        el1['distributor_id'] = 'somerandomstring'
        result = el1.save()
        self.assertIn('distributor_id', result['errors'])
        self.assertEqual(len(PartDistributor.all()), 0)
        # now with valid id it is possible to save
        el1['distributor_id'] = self.did
        result = el1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(PartDistributor.all()), 1)

    def test_desc_notnone(self):
        self.assertEqual(len(PartDistributor.all()), 0)
        # notnone
        element = PartDistributor({'part_id': self.pid, 'distributor_id': self.did, 'desc': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['desc'])
        self.assertEqual(len(PartDistributor.all()), 0)
        # working
        element['desc'] = 'text'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(PartDistributor.all()), 1)

    def test_order_no_notnone(self):
        self.assertEqual(len(PartDistributor.all()), 0)
        # notnone
        element = PartDistributor({'part_id': self.pid, 'distributor_id': self.did, 'order_no': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['order_no'])
        self.assertEqual(len(PartDistributor.all()), 0)
        # working
        element['order_no'] = 'text'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(PartDistributor.all()), 1)

    def test_url_notnone(self):
        self.assertEqual(len(PartDistributor.all()), 0)
        # notnone
        element = PartDistributor({'part_id': self.pid, 'distributor_id': self.did, 'url': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['url'])
        self.assertEqual(len(PartDistributor.all()), 0)
        # working
        element['url'] = 'text'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(PartDistributor.all()), 1)

    def test_pkg_price_float_and_notnone(self):
        self.assertEqual(len(PartDistributor.all()), 0)
        # notnone
        element = PartDistributor({'part_id': self.pid, 'distributor_id': self.did, 'pkg_price': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['pkg_price'])
        self.assertEqual(len(PartDistributor.all()), 0)
        # float
        element = PartDistributor({'part_id': self.pid, 'distributor_id': self.did, 'pkg_price': '1.23'})
        result = element.save()
        self.assertIn('type', result['errors']['pkg_price'])
        self.assertEqual(len(PartDistributor.all()), 0)
        # working
        element['pkg_price'] = 1.23
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(PartDistributor.all()), 1)

    def test_pkg_units_int_and_notnone(self):
        self.assertEqual(len(PartDistributor.all()), 0)
        # notnone
        element = PartDistributor({'part_id': self.pid, 'distributor_id': self.did, 'pkg_units': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['pkg_units'])
        self.assertEqual(len(PartDistributor.all()), 0)
        # float
        element = PartDistributor({'part_id': self.pid, 'distributor_id': self.did, 'pkg_units': '2'})
        result = element.save()
        self.assertIn('type', result['errors']['pkg_units'])
        self.assertEqual(len(PartDistributor.all()), 0)
        # working
        element['pkg_units'] = 2
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(PartDistributor.all()), 1)

    def test_preferred_bool_and_notnone(self):
        self.assertEqual(len(PartDistributor.all()), 0)
        # notnone
        element = PartDistributor({'part_id': self.pid, 'distributor_id': self.did, 'preferred': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['preferred'])
        self.assertEqual(len(PartDistributor.all()), 0)
        # float
        element = PartDistributor({'part_id': self.pid, 'distributor_id': self.did, 'preferred': 'true'})
        result = element.save()
        self.assertIn('type', result['errors']['preferred'])
        self.assertEqual(len(PartDistributor.all()), 0)
        # working
        element['preferred'] = True
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(PartDistributor.all()), 1)

    def test_deletion(self):
        el1 = PartDistributor({'part_id': self.pid, 'distributor_id': self.did})
        el1.save()
        el2 = PartDistributor({'part_id': self.pid, 'distributor_id': self.did})
        el2.save()
        self.assertEqual(len(PartDistributor.all()), 2)
        el1.delete()
        self.assertEqual(len(PartDistributor.all()), 1)
        el2.delete()
        self.assertEqual(len(PartDistributor.all()), 0)

    def test_only_one_preferred_exists(self):
        # first one gets preferred
        el1 = PartDistributor({'part_id': self.pid, 'distributor_id': self.did})
        self.assertFalse(el1['preferred'])
        el1.save()
        self.assertTrue(el1['preferred'])
        # new one is set to be preferred
        el2 = PartDistributor({'part_id': self.pid, 'distributor_id': self.did, 'preferred': True})
        el2.save()
        el1.reload()
        self.assertFalse(el1['preferred'])
        self.assertTrue(el2['preferred'])
        # new one is not the new preferred, and does not change the preferred
        el3 = PartDistributor({'part_id': self.pid, 'distributor_id': self.did})
        el3.save()
        el1.reload()
        el2.reload()
        self.assertFalse(el1['preferred'])
        self.assertTrue(el2['preferred'])
        self.assertFalse(el3['preferred'])

    def test_deletion_of_preferred(self):
        el1 = PartDistributor({'part_id': self.pid, 'distributor_id': self.did})
        el1.save()
        el2 = PartDistributor({'part_id': self.pid, 'distributor_id': self.did, 'preferred': True})
        el2.save()
        el3 = PartDistributor({'part_id': self.pid, 'distributor_id': self.did})
        el3.save()
        el1.reload()
        el2.reload()
        el3.reload()
        self.assertFalse(el1['preferred'])
        self.assertTrue(el2['preferred'])
        self.assertFalse(el3['preferred'])
        # deleting non preferred, does not change the preferred
        el3.delete()
        el2.reload()
        el1.reload()
        self.assertFalse(el1['preferred'])
        self.assertTrue(el2['preferred'])
        # deleting preferred promotes a random one to be preferred
        el2.delete()
        el1.reload()
        self.assertTrue(el1['preferred'])
        # deleting last one does not produce an error
        result = el1.delete()
        self.assertNotIn('error', result)


setup_module = setUpModule
teardown_module = tearDownModule


class TestPartDistributorApi(ApiTestBase):
    _element = PartDistributor
    _path = 'partdistributor'
    _patch_valid = {'desc': 'Milli Meters'}
    _patch_invalid = {'preferred': 'typestring'}

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
