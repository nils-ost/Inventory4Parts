import unittest
from helpers.docdb import docDB
from elements import Part, Unit, Category, Footprint, MountingStyle


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
        # if unit_id is not a valid id if can't be saved
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
        # if footprint_id is not a valid id if can't be saved
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
        # if mounting_style_id is not a valid id if can't be saved
        p2 = Part({'name': 'somepart', 'category_id': self.c1, 'unit_id': self.u1, 'mounting_style_id': 'somerandomstring'})
        result = p2.save()
        self.assertIn('mounting_style_id', result['errors'])
        self.assertEqual(len(Part.all()), 1)
        # now with valid id it is possible to save
        p2['mounting_style_id'] = self.ms1
        result = p2.save()
        self.assertNotIn('errors', result)
        self.assertEqual(len(Part.all()), 2)
        self.assertTrue(False)

    def test_category_id_FK_and_notnone(self):
        self.assertEqual(len(Part.all()), 0)
        # if category_id is None it can't be saved
        p1 = part('name': 'somepart', 'unit_id': self.u1, 'category_id': None)
        result = p1.save()
        self.assertIn('category_id', result['errors'])
        self.assertEqual(len(Part.all()), 0)
        # if category_id is not a valid id if can't be saved
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
