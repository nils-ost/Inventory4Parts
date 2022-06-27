import unittest
from helpers.docdb import docDB
from elements import MountingStyle, Footprint
from testcases._wrapper import ApiTestBase, setUpModule, tearDownModule


class TestMountingStyle(unittest.TestCase):
    def test_name_uniqeness(self):
        docDB.clear()
        self.assertEqual(len(MountingStyle.all()), 0)
        ms1 = MountingStyle()
        ms1['name'] = 'SMD'
        result = ms1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(MountingStyle.all()), 1)
        ms2 = MountingStyle()
        ms2['name'] = 'SMD'
        result = ms2.save()
        self.assertIn('errors', result)
        self.assertEqual(len(MountingStyle.all()), 1)
        ms2['name'] = 'THD'
        result = ms2.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(MountingStyle.all()), 2)

    def test_name_notnone(self):
        docDB.clear()
        self.assertEqual(len(MountingStyle.all()), 0)
        ms1 = MountingStyle()
        ms1['name'] = 'SMD'
        result = ms1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(MountingStyle.all()), 1)
        ms2 = MountingStyle()
        result = ms2.save()
        self.assertIn('errors', result)
        self.assertEqual(len(MountingStyle.all()), 1)
        ms2['name'] = 'THD'
        result = ms2.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(MountingStyle.all()), 2)

    def test_feeding_attr_on_init(self):
        docDB.clear()
        self.assertEqual(len(MountingStyle.all()), 0)
        ms1 = MountingStyle({'name': 'SMD', 'desc': 'Surface Mount'})
        result = ms1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(MountingStyle.all()), 1)
        self.assertEqual(ms1['name'], 'SMD')
        self.assertEqual(ms1['desc'], 'Surface Mount')
        ms2 = MountingStyle({'name': 'THD', 'desc': 'Through Hole', 'some': 'random'})
        result = ms2.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(MountingStyle.all()), 2)
        self.assertEqual(ms2['name'], 'THD')
        self.assertEqual(ms2['desc'], 'Through Hole')
        self.assertEqual(len(ms2._attr), 3)  # name, desc and _id

    def test_deletion(self):
        docDB.clear()
        ms1 = MountingStyle({'name': 'SMD', 'desc': 'Surface Mount'})
        ms1.save()
        ms2 = MountingStyle({'name': 'THD', 'desc': 'Through Hole'})
        ms2.save()
        self.assertEqual(len(MountingStyle.all()), 2)
        self.assertIsNotNone(ms1['_id'])
        self.assertIsNotNone(ms1['name'])
        self.assertIsNotNone(ms1['desc'])
        # delete valid one
        ms1.delete()
        self.assertEqual(len(MountingStyle.all()), 1)
        self.assertIsNone(ms1['_id'])
        self.assertIsNone(ms1['name'])
        self.assertEqual(ms1['desc'], '')
        # try deleting unsaved one
        ms3 = MountingStyle({'name': 'THD'})
        self.assertIsNotNone(ms3['name'])
        ms3.delete()
        self.assertEqual(len(MountingStyle.all()), 1)
        self.assertIsNone(ms3['name'])
        # try deleting with invalid _id
        ms4 = MountingStyle({'_id': 'invalid', 'name': 'THD'})
        self.assertIsNotNone(ms4['_id'])
        self.assertIsNotNone(ms4['name'])
        ms4.delete()
        self.assertEqual(len(MountingStyle.all()), 1)
        self.assertIsNone(ms4['_id'])
        self.assertIsNone(ms4['name'])

    def test_updating_desc(self):
        docDB.clear()
        ms1 = MountingStyle({'name': 'SMD', 'desc': 'Surface Mou'})
        ms1.save()
        self.assertEqual(len(MountingStyle.all()), 1)
        ms_fromdb = MountingStyle.get(ms1['_id'])
        self.assertEqual(ms_fromdb['desc'], 'Surface Mou')
        ms1['desc'] = 'Surface Mount'
        ms1.save()
        self.assertEqual(len(MountingStyle.all()), 1)
        ms_fromdb.reload()
        self.assertEqual(ms_fromdb['desc'], 'Surface Mount')

    def test_deletion_with_associated_footprint(self):
        # if a Footprint referes to a MountingStyle the mounting_style_id should be None'ed when MountingStyle is deleted
        docDB.clear()
        ms = MountingStyle({'name': 'SMD'})
        ms.save()
        fp = Footprint({'name': '0806', 'mounting_style_id': ms['_id']})
        fp.save()
        self.assertEqual(fp['mounting_style_id'], ms['_id'])
        ms.delete()
        fp.reload()
        self.assertIsNone(fp['mounting_style_id'])

    def test_deletion_with_associated_part(self):
        # if Part referes to a MountingStyle the mounting_style_id should be None'ed when MountingStyle is deleted
        self.assertTrue(False)


setup_module = setUpModule
teardown_module = tearDownModule


class TestMountingStyleApi(ApiTestBase):
    _element = MountingStyle
    _path = 'mountingstyle'
    _setup_el1 = {'name': 'SMD'}
    _setup_el2 = {'name': 'THD'}
    _post_valid = {'name': 'something'}
    _patch_valid = {'desc': 'hello world'}
    _patch_invalid = {'name': None}
