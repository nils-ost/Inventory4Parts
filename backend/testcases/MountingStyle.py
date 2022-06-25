import unittest
from helpers.docdb import docDB
from elements import MountingStyle, Footprint
from testcases._wrapper import ApiTestBase, setUpModule, tearDownModule

setup_module = setUpModule
teardown_module = tearDownModule


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


class TestMountingStyleApi(ApiTestBase):
    def setUp(self):
        docDB.clear()
        ms = MountingStyle({'name': 'SMD'})
        self.id1 = ms.save().get('created')
        ms = MountingStyle({'name': 'THD'})
        self.id2 = ms.save().get('created')

    def test_options_all(self):
        result = self.webapp_request(path='/mountingstyle/', method='OPTIONS')
        self.assertIn('OPTIONS', result.headers['Allow'])
        self.assertIn('GET', result.headers['Allow'])
        self.assertIn('POST', result.headers['Allow'])
        self.assertNotIn('PATCH', result.headers['Allow'])
        self.assertNotIn('DELETE', result.headers['Allow'])
        self.assertNotIn('PUT', result.headers['Allow'])

    def test_options_single(self):
        result = self.webapp_request(path='/mountingstyle/something/', method='OPTIONS')
        self.assertTrue(result.status.startswith('404'), msg=f'should start with 404 but is {result.status}')
        result = self.webapp_request(path=f'/mountingstyle/{self.id1}/', method='OPTIONS')
        self.assertIn('OPTIONS', result.headers['Allow'])
        self.assertIn('GET', result.headers['Allow'])
        self.assertNotIn('POST', result.headers['Allow'])
        self.assertIn('PATCH', result.headers['Allow'])
        self.assertIn('DELETE', result.headers['Allow'])
        self.assertNotIn('PUT', result.headers['Allow'])

    def test_get_all(self):
        result = self.webapp_request(path='/mountingstyle/', method='GET')
        self.assertEqual(len(result.json), 2)

    def test_get_single(self):
        result = self.webapp_request(path=f'/mountingstyle/{self.id1}/', method='GET')
        self.assertEqual(result.json['name'], 'SMD')
        result = self.webapp_request(path='/mountingstyle/something/', method='GET')
        self.assertTrue(result.status.startswith('404'), msg=f'should start with 404 but is {result.status}')

    def test_post_all(self):
        self.assertEqual(len(MountingStyle.all()), 2)
        result = self.webapp_request(path='/mountingstyle/', method='POST')
        self.assertTrue(result.status.startswith('400'), msg=f'should start with 400 but is {result.status}')
        self.assertEqual(len(MountingStyle.all()), 2)
        result = self.webapp_request(path='/mountingstyle/', method='POST', data=['a', 'list'])
        self.assertTrue(result.status.startswith('400'), msg=f'should start with 400 but is {result.status}')
        self.assertEqual(len(MountingStyle.all()), 2)
        result = self.webapp_request(path='/mountingstyle/', method='POST', name='something')
        self.assertTrue(result.status.startswith('201'), msg=f'should start with 201 but is {result.status}')
        self.assertEqual(len(MountingStyle.all()), 3)

    def test_post_single(self):
        result = self.webapp_request(path=f'/mountingstyle/{self.id1}/', method='POST')
        self.assertTrue(result.status.startswith('405'), msg=f'should start with 405 but is {result.status}')

    def test_delete_all(self):
        result = self.webapp_request(path='/mountingstyle/', method='DELETE')
        self.assertTrue(result.status.startswith('405'), msg=f'should start with 405 but is {result.status}')

    def test_delete_single(self):
        self.assertEqual(len(MountingStyle.all()), 2)
        result = self.webapp_request(path=f'/mountingstyle/{self.id1}/', method='DELETE')
        self.assertEqual(len(MountingStyle.all()), 1)
        result = self.webapp_request(path=f'/mountingstyle/{self.id1}/', method='DELETE')
        self.assertTrue(result.status.startswith('404'), msg=f'should start with 404 but is {result.status}')
        self.assertEqual(len(MountingStyle.all()), 1)
        result = self.webapp_request(path=f'/mountingstyle/{self.id2}/', method='DELETE')
        self.assertEqual(len(MountingStyle.all()), 0)

    def test_patch_all(self):
        result = self.webapp_request(path='/mountingstyle/', method='PATCH')
        self.assertTrue(result.status.startswith('405'), msg=f'should start with 405 but is {result.status}')

    def test_patch_single(self):
        ms = MountingStyle.get(self.id1)
        self.assertEqual(ms['desc'], '')
        result = self.webapp_request(path=f'/mountingstyle/{self.id1}/', method='PATCH', desc='hello world')
        ms.reload()
        self.assertEqual(ms['desc'], 'hello world')
        result = self.webapp_request(path='/mountingstyle/something/', method='PATCH', desc='hello world')
        self.assertTrue(result.status.startswith('404'), msg=f'should start with 404 but is {result.status}')
        result = self.webapp_request(path=f'/mountingstyle/{self.id1}/', method='PATCH', data=['a', 'list'])
        self.assertTrue(result.status.startswith('400'), msg=f'should start with 400 but is {result.status}')
        result = self.webapp_request(path=f'/mountingstyle/{self.id1}/', method='PATCH', name=None)
        self.assertTrue(result.status.startswith('400'), msg=f'should start with 400 but is {result.status}')
        ms.reload()
        self.assertIsNotNone(ms['name'])

    def test_put_all(self):
        result = self.webapp_request(path='/mountingstyle/', method='PUT')
        self.assertTrue(result.status.startswith('405'), msg=f'should start with 405 but is {result.status}')
        self.assertIn('OPTIONS', result.headers['Allow'])
        self.assertIn('GET', result.headers['Allow'])
        self.assertIn('POST', result.headers['Allow'])

    def test_put_single(self):
        result = self.webapp_request(path=f'/mountingstyle/{self.id1}/', method='PUT')
        self.assertTrue(result.status.startswith('405'), msg=f'should start with 405 but is {result.status}')
        self.assertIn('OPTIONS', result.headers['Allow'])
        self.assertIn('GET', result.headers['Allow'])
        self.assertIn('PATCH', result.headers['Allow'])
        self.assertIn('DELETE', result.headers['Allow'])
