import unittest
from helpers.docdb import docDB
from elements import Unit, Category, Part
from testcases._wrapper import ApiTestBase, setUpModule, tearDownModule


class TestUnit(unittest.TestCase):
    def test_name_uniqeness_and_notnone(self):
        docDB.clear()
        self.assertEqual(len(Unit.all()), 0)
        element = Unit({'name': 'Name1'})
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Unit.all()), 1)
        # notnone
        element = Unit()
        result = element.save()
        self.assertIn('name', result['errors'])
        self.assertEqual(len(Unit.all()), 1)
        # unique
        element['name'] = 'Name1'
        result = element.save()
        self.assertIn('name', result['errors'])
        self.assertEqual(len(Unit.all()), 1)
        # working
        element['name'] = 'Name2'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Unit.all()), 2)

    def test_default_bool_and_notnone(self):
        docDB.clear()
        element = Unit({'name': 'Name1'})
        # notnone
        element['default'] = None
        result = element.save()
        self.assertIn('not to be None', result['errors']['default'])
        # other type than bool
        element['default'] = 'hi'
        result = element.save()
        self.assertIn('type', result['errors']['default'])
        # working
        element['default'] = True
        result = element.save()
        self.assertNotIn('errors', result)

    def test_only_one_default_exists(self):
        docDB.clear()
        # first one gets default
        el1 = Unit({'name': 'mm'})
        self.assertFalse(el1['default'])
        el1.save()
        self.assertTrue(el1['default'])
        # new one is set to be default
        el2 = Unit({'name': 'pcs', 'default': True})
        el2.save()
        el1.reload()
        self.assertFalse(el1['default'])
        self.assertTrue(el2['default'])
        # new one is not the new default, and does not change the default
        el3 = Unit({'name': 'cm'})
        el3.save()
        el1.reload()
        el2.reload()
        self.assertFalse(el1['default'])
        self.assertTrue(el2['default'])
        self.assertFalse(el3['default'])

    def test_deletion_of_default(self):
        docDB.clear()
        el1 = Unit({'name': 'mm'})
        el1.save()
        el2 = Unit({'name': 'pcs', 'default': True})
        el2.save()
        el3 = Unit({'name': 'cm'})
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
        el1.delete()

    def test_deletion_with_associated_part(self):
        # if Part referes to a Unit the Unit shouldn't be deletable
        docDB.clear()
        u = Unit({'name': 'someunit'})
        u.save()
        self.assertNotNone(u['_id'])
        c = Category({'name': 'somecat'})
        c.save()
        self.assertNotNone(c['_id'])
        p = Part('name': 'somepart', unit_id=u['_id'], category_id=c['_id'])
        p.save()
        self.assertNotNone(p['_id'])
        self.assertEqual(len(Unit.all()), 1)
        # it shouldn be possible to delete Unit because of associated Part
        result = u.delete()
        self.assertIn('error', result)
        self.assertEqual(len(Unit.all()), 1)
        # deleting Part should make it possible to delete Unit
        p.delete()
        result = u.delete()
        self.asserNotIn('error', result)
        self.assertEqual(len(Unit.all()), 0)


setup_module = setUpModule
teardown_module = tearDownModule


class TestUnitApi(ApiTestBase):
    _element = Unit
    _path = 'unit'
    _setup_el1 = {'name': 'mm'}
    _setup_el2 = {'name': 'pcs'}
    _post_valid = {'name': 'cm'}
    _patch_valid = {'desc': 'Milli Meters'}
    _patch_invalid = {'default': 'typestring'}
