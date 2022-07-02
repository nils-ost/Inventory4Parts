import unittest
from helpers.docdb import docDB
from elements import StorageGroup, StorageLocation
from testcases._wrapper import ApiTestBase, setUpModule, tearDownModule


class TestStorageGroup(unittest.TestCase):
    def test_name_uniqeness_and_notnone(self):
        docDB.clear()
        self.assertEqual(len(StorageGroup.all()), 0)
        element = StorageGroup({'name': 'Name1'})
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StorageGroup.all()), 1)
        # notnone
        element = StorageGroup()
        result = element.save()
        self.assertIn('name', result['errors'])
        self.assertEqual(len(StorageGroup.all()), 1)
        # unique
        element['name'] = 'Name1'
        result = element.save()
        self.assertIn('name', result['errors'])
        self.assertEqual(len(StorageGroup.all()), 1)
        # working
        element['name'] = 'Name2'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StorageGroup.all()), 2)

    def test_desc_notnone(self):
        docDB.clear()
        self.assertEqual(len(StorageGroup.all()), 0)
        # notnone
        element = StorageGroup({'name': 'Name1', 'desc': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['desc'])
        self.assertEqual(len(StorageGroup.all()), 0)
        # working
        element['desc'] = 'text'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StorageGroup.all()), 1)

    def test_deletion(self):
        docDB.clear()
        el1 = StorageGroup({'name': 'Name1'})
        el1.save()
        el2 = StorageGroup({'name': 'Name2'})
        el2.save()
        self.assertEqual(len(StorageGroup.all()), 2)
        el1.delete()
        self.assertEqual(len(StorageGroup.all()), 1)
        el2.delete()
        self.assertEqual(len(StorageGroup.all()), 0)

    def test_deletion_with_associated_storage_location(self):
        # if StorageLocations refer to StorageGroup, the deletion of StorageGroup causes the StorageLocations reference to be None'ed
        docDB.clear()
        sg1 = StorageGroup({'name': 'Name1'})
        sg1.save()
        sg2 = StorageGroup({'name': 'Name2'})
        sg2.save()
        sl1 = StorageLocation({'name': 'Name1', 'storage_group_id': sg1['_id']})
        sl1.save()
        sl2 = StorageLocation({'name': 'Name2', 'storage_group_id': sg2['_id']})
        sl2.save()
        self.assertIsNotNone(sl1['storage_group_id'])
        self.assertIsNotNone(sl2['storage_group_id'])
        sg1.delete()
        sl1.reload()
        sl2.reload()
        self.assertIsNone(sl1['storage_group_id'])
        self.assertIsNotNone(sl2['storage_group_id'])
        sg2.delete()
        sl1.reload()
        sl2.reload()
        self.assertIsNone(sl1['storage_group_id'])
        self.assertIsNone(sl2['storage_group_id'])


setup_module = setUpModule
teardown_module = tearDownModule


class TestStorageGroupApi(ApiTestBase):
    _element = StorageGroup
    _path = 'storagegroup'
    _setup_el1 = {'name': 'Name1'}
    _setup_el2 = {'name': 'Name2'}
    _post_valid = {'name': 'Name3'}
    _patch_valid = {'desc': 'Text'}
    _patch_invalid = {'desc': None}
