import unittest
from helpers.docdb import docDB
# from elements import Part


class TestPart(unittest.TestCase):
    def setUp(self):
        docDB.clear()

    def test_name_notnone(self):
        self.assertTrue(False)

    def test_unit_id_FK_and_notnone(self):
        self.assertTrue(False)

    def test_footprint_id_FK_or_None(self):
        self.assertTrue(False)

    def test_mounting_style_id_FK_or_None(self):
        self.assertTrue(False)

    def test_category_id_FK_and_notnone(self):
        self.assertTrue(False)

    def test_footprint_overwrites_mounting_style(self):
        self.assertTrue(False)
