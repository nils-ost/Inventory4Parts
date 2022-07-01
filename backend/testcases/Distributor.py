import unittest
from helpers.docdb import docDB
from elements import Distributor, PartDistributor, Part, Unit, Category
from testcases._wrapper import ApiTestBase, setUpModule, tearDownModule


class TestDistributor(unittest.TestCase):
    def test_name_uniqeness_and_notnone(self):
        docDB.clear()
        self.assertEqual(len(Distributor.all()), 0)
        element = Distributor({'name': 'Name1'})
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Distributor.all()), 1)
        # notnone
        element = Distributor()
        result = element.save()
        self.assertIn('name', result['errors'])
        self.assertEqual(len(Distributor.all()), 1)
        # unique
        element['name'] = 'Name1'
        result = element.save()
        self.assertIn('name', result['errors'])
        self.assertEqual(len(Distributor.all()), 1)
        # working
        element['name'] = 'Name2'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Distributor.all()), 2)

    def test_desc_notnone(self):
        docDB.clear()
        self.assertEqual(len(Distributor.all()), 0)
        # notnone
        element = Distributor({'name': 'Name1', 'desc': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['desc'])
        self.assertEqual(len(Distributor.all()), 0)
        # working
        element['desc'] = 'text'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Distributor.all()), 1)

    def test_url_notnone(self):
        docDB.clear()
        self.assertEqual(len(Distributor.all()), 0)
        # notnone
        element = Distributor({'name': 'Name1', 'url': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['url'])
        self.assertEqual(len(Distributor.all()), 0)
        # working
        element['url'] = 'text'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Distributor.all()), 1)

    def test_deletion(self):
        # if distributor is deleted all referred PartDistrubutor should also be deleted
        docDB.clear()
        u = Unit({'name': 'u'})
        u.save()
        c = Category({'name': 'c'})
        c.save()
        p = Part({'name': 'p', 'unit_id': u['_id'], 'category_id': c['_id']})
        result = p.save()
        self.assertNotIn('errors', result)
        d1 = Distributor({'name': 'd1'})
        d1.save()
        d2 = Distributor({'name': 'd2'})
        d2.save()
        pd1 = PartDistributor({'distributor_id': d1['_id'], 'part_id': p['_id']})
        pd1.save()
        pd2 = PartDistributor({'distributor_id': d2['_id'], 'part_id': p['_id']})
        pd2.save()
        self.assertEqual(len(Distributor.all()), 2)
        self.assertEqual(len(PartDistributor.all()), 2)
        d1.delete()
        self.assertEqual(len(Distributor.all()), 1)
        self.assertEqual(len(PartDistributor.all()), 1)


setup_module = setUpModule
teardown_module = tearDownModule


class TestDistributorApi(ApiTestBase):
    _element = Distributor
    _path = 'distributor'
    _setup_el1 = {'name': 'Name1'}
    _setup_el2 = {'name': 'Name2'}
    _post_valid = {'name': 'Name3'}
    _patch_valid = {'desc': 'Text'}
    _patch_invalid = {'url': None}
