import unittest
from helpers.docdb import docDB
from elements import StorageGroup, StorageLocation, Unit, Category, Part, PartLocation
from testcases._wrapper import ApiTestBase, setUpModule, tearDownModule


class TestStorageLocation(unittest.TestCase):
    def test_name_notnone(self):
        docDB.clear()
        self.assertEqual(len(StorageLocation.all()), 0)
        # notnone
        element = StorageLocation({'name': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['name'])
        self.assertEqual(len(StorageLocation.all()), 0)
        # working
        element['name'] = 'text'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StorageLocation.all()), 1)

    def test_desc_notnone(self):
        docDB.clear()
        self.assertEqual(len(StorageLocation.all()), 0)
        # notnone
        element = StorageLocation({'name': 'Name1', 'desc': None})
        result = element.save()
        self.assertIn('not to be None', result['errors']['desc'])
        self.assertEqual(len(StorageLocation.all()), 0)
        # working
        element['desc'] = 'text'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StorageLocation.all()), 1)

    def test_parent_storage_location_id_FK_or_none(self):
        docDB.clear()
        self.assertEqual(len(StorageLocation.all()), 0)
        # if parent_storage_location_id is None it can be saved
        el1 = StorageLocation({'name': 'Name1', 'parent_storage_location_id': None})
        result = el1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StorageLocation.all()), 1)
        # if parent_storage_location_id can't be it's own id
        el1['parent_storage_location_id'] = el1['_id']
        result = el1.save()
        self.assertIn('parent_storage_location_id', result['errors'])
        self.assertEqual(len(StorageLocation.all()), 1)
        # if parent_storage_location_id is not a valid id it can't be saved
        el2 = StorageLocation({'name': 'Name2', 'parent_storage_location_id': 'somerandomstring'})
        result = el2.save()
        self.assertIn('parent_storage_location_id', result['errors'])
        self.assertEqual(len(StorageLocation.all()), 1)
        # now with valid id it is possible to save
        el2['parent_storage_location_id'] = el1['_id']
        result = el2.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StorageLocation.all()), 2)

    def test_storage_group_id_FK_or_none(self):
        docDB.clear()
        sg = StorageGroup({'name': 'Name1'})
        sg.save()
        self.assertEqual(len(StorageLocation.all()), 0)
        # if storage_group_id is None it can be saved
        el1 = StorageLocation({'name': 'Name1', 'storage_group_id': None})
        result = el1.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StorageLocation.all()), 1)
        # if storage_group_id is not a valid id it can't be saved
        el2 = StorageLocation({'name': 'Name2', 'storage_group_id': 'somerandomstring'})
        result = el2.save()
        self.assertIn('storage_group_id', result['errors'])
        self.assertEqual(len(StorageLocation.all()), 1)
        # now with valid id it is possible to save
        el2['storage_group_id'] = sg['_id']
        result = el2.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(StorageLocation.all()), 2)

    def test_deletion(self):
        docDB.clear()
        el1 = StorageLocation({'name': 'Name1'})
        el1.save()
        el2 = StorageLocation({'name': 'Name2'})
        el2.save()
        self.assertEqual(len(StorageLocation.all()), 2)
        el1.delete()
        self.assertEqual(len(StorageLocation.all()), 1)
        el2.delete()
        self.assertEqual(len(StorageLocation.all()), 0)

    def test_deletion_with_associated_parent(self):
        # if a parent is deleted it's childs should get parent_storage_location_id None'ed
        docDB.clear()
        parent1 = StorageLocation({'name': 'Name1'})
        parent1.save()
        parent2 = StorageLocation({'name': 'Name2'})
        parent2.save()
        child1 = StorageLocation({'name': 'Name3', 'parent_storage_location_id': parent1['_id']})
        child1.save()
        child2 = StorageLocation({'name': 'Name4', 'parent_storage_location_id': parent2['_id']})
        child2.save()
        self.assertIsNotNone(child1['parent_storage_location_id'])
        self.assertIsNotNone(child2['parent_storage_location_id'])
        parent1.delete()
        child1.reload()
        child2.reload()
        self.assertIsNone(child1['parent_storage_location_id'])
        self.assertIsNotNone(child2['parent_storage_location_id'])
        parent2.delete()
        child1.reload()
        child2.reload()
        self.assertIsNone(child1['parent_storage_location_id'])
        self.assertIsNone(child2['parent_storage_location_id'])

    def test_deletion_with_associated_partlocation(self):
        # if StorageLocation is deleted all referred PartLocation should also be deleted
        u = Unit({'name': 'Name1'})
        u.save()
        c = Category({'name': 'Name1'})
        c.save()
        p = Part({'unit_id': u['_id'], 'category_id': c['_id'], 'name': 'somename1'})
        p.save()
        sl1 = StorageLocation({'name': 'Name1'})
        sl1.save()
        sl2 = StorageLocation({'name': 'Name2'})
        sl2.save()
        pl1 = PartLocation({'storage_location_id': sl1['_id'], 'part_id': p['_id']})
        pl1.save()
        pl2 = PartLocation({'storage_location_id': sl2['_id'], 'part_id': p['_id']})
        pl2.save()
        self.assertEqual(len(PartLocation.all()), 2)
        self.assertEqual(len(PartLocation.all()), 2)
        sl1.delete()
        self.assertEqual(len(PartLocation.all()), 1)
        self.assertEqual(len(PartLocation.all()), 1)
        sl2.delete()
        self.assertEqual(len(PartLocation.all()), 0)
        self.assertEqual(len(PartLocation.all()), 0)


setup_module = setUpModule
teardown_module = tearDownModule


class TestStorageLocationApi(ApiTestBase):
    _element = StorageLocation
    _path = 'storagelocation'
    _setup_el1 = {'name': 'Name1'}
    _setup_el2 = {'name': 'Name2'}
    _post_valid = {'name': 'Name3'}
    _patch_valid = {'desc': 'Text'}
    _patch_invalid = {'desc': None}
