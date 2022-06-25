import unittest
from helpers.docdb import docDB
from elements import Footprint, MountingStyle


class TestFootprint(unittest.TestCase):
    def test_name_uniqeness_and_notnone(self):
        docDB.clear()
        self.assertEqual(len(Footprint.all()), 0)
        element = Footprint({'name': 'Name1'})
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Footprint.all()), 1)
        # notnone
        element = Footprint()
        result = element.save()
        self.assertIn('name', result['errors'])
        self.assertEqual(len(Footprint.all()), 1)
        # unique
        element['name'] = 'Name1'
        result = element.save()
        self.assertIn('name', result['errors'])
        self.assertEqual(len(Footprint.all()), 1)
        # working
        element['name'] = 'Name2'
        result = element.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Footprint.all()), 2)

    def test_mounting_style_id_is_validated(self):
        docDB.clear()
        # can be None
        fp = Footprint({'name': '0806'})
        self.assertIsNone(fp['mounting_style_id'])
        result = fp.save()
        self.assertNotIn('errors', result)
        # can't be random
        fp['mounting_style_id'] = 'some random'
        result = fp.save()
        self.assertIn('mounting_style_id', result['errors'])
        # can be valid MountingStyle
        ms = MountingStyle({'name': 'SMD'})
        ms.save()
        fp['mounting_style_id'] = ms['_id']
        result = fp.save()
        self.assertNotIn('errors', result)
