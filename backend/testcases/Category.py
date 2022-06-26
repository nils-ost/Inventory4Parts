import unittest
from helpers.docdb import docDB
from elements import Category
from testcases._wrapper import ApiTestBase, setUpModule, tearDownModule


class TestCategory(unittest.TestCase):
    def test_name_notnone(self):
        docDB.clear()
        self.assertEqual(len(Category.all()), 0)
        element = Category({'name': 'Name1'})
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Category.all()), 1)
        # notnone
        element = Category()
        result = element.save()
        self.assertIn('name', result['errors'])
        self.assertEqual(len(Category.all()), 1)
        # not unique - working
        element['name'] = 'Name1'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Category.all()), 2)
        # working
        element['name'] = 'Name2'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Category.all()), 2)

    def test_parent_category_id_is_validated(self):
        docDB.clear()
        # can be None
        child = Category({'name': 'child'})
        self.assertIsNone(child['parent_category_id'])
        result = child.save()
        self.assertNotIn('errors', result)
        # can't be random
        child['parent_category_id'] = 'some random'
        result = child.save()
        self.assertIn('parent_category_id', result['errors'])
        # can't be self
        child['parent_category_id'] = child['_id']
        result = child.save()
        self.assertIn('parent_category_id', result['errors'])
        # can be valid Category
        parent = Category({'name': 'parent'})
        parent.save()
        child['parent_category_id'] = parent['_id']
        result = child.save()
        self.assertNotIn('errors', result)
        self.assertIsNotNone(child['parent_category_id'])

    def test_deletion_with_associated_child_category(self):
        # if a category does have a parent category, and this is deleted, the category should no longer have a parent category
        docDB.clear()
        parent = Category({'name': 'parent'})
        parent.save()
        child = Category({'name': 'child', 'parent_category_id': parent['_id']})
        child.save()
        child.reload()
        self.assertEqual(len(Category.all()), 2)
        self.assertEqual(child['parent_category_id'], parent['_id'])
        parent.delete()
        child.reload()
        self.assertEqual(len(Category.all()), 1)
        self.assertIsNone(child['parent_category_id'])


setup_module = setUpModule
teardown_module = tearDownModule


class TestCategoryApi(ApiTestBase):
    _element = Category
    _path = 'category'
    _setup_el1 = {'name': 'Passive'}
    _setup_el2 = {'name': 'Active'}
    _post_valid = {'name': 'Wires'}
    _patch_valid = {'desc': 'hello world'}
    _patch_invalid = {'name': None}
