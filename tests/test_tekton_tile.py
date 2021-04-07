from testing_common import tekton, load_test_data_dir, int_list_to_bytes
from tekton import tekton_tile
import os
import unittest

class TestTektonTile(unittest.TestCase):
    def test_init(self):
        test_tile = tekton_tile.TektonTile()
        self.assertTrue(isinstance(test_tile, tekton_tile.TektonTile))
        self.assertEqual(test_tile.bts_type, 0x00, "Test Tile BTS Type is not 0x00.")
        self.assertEqual(test_tile.bts_num, 0x00, "Test Tile BTS Number is not 0x00.")
        self.assertFalse(test_tile.h_mirror, "Test Tile Horizontal Mirror is not False.")
        self.assertFalse(test_tile.v_mirror, "Test Tile Vertical Mirror is not False.")
        self.assertEqual(test_tile._tileno, 0x00, "Test Tile _tileno is not 0x00.")

    def test_eq(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_tile',
                                     'test_eq'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_tile_left, test_tile_right = self._populate_bin_op_operands(test_item)
            self.assertEqual(test_tile_left, test_tile_right, "Tiles should be equal but they aren't!")

        test_tile = tekton_tile.TektonTile()
        with self.assertRaises(TypeError):
            test_tile == "A string"

    def test_ne(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_tile',
                                     'test_ne'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_tile_left, test_tile_right = self._populate_bin_op_operands(test_item)
            self.assertNotEqual(test_tile_left, test_tile_right, "Tiles should not be equal but they are!")

        test_tile = tekton_tile.TektonTile()
        with self.assertRaises(TypeError):
            test_tile != "A string"

    def test_tileno(self):
        test_tile = tekton_tile.TektonTile()
        test_tile.tileno = 0x10a
        expected_result = 0x10a

        self.assertEqual(expected_result, test_tile.tileno, "Test Tile tileno property did not return correct value!")

        with self.assertRaises(TypeError,
                               msg="TektonTile.tileno should only accept int, but it accepted string!"):
            test_tile.tileno = "rock"
        with self.assertRaises(ValueError,
                               msg="TektonTile.tileno allowed a value larger than 0x3ff, but it should not have!"):
            test_tile.tileno = 0x400
        with self.assertRaises(ValueError,
                               msg="TektonTile.tileno allowed a value smaller than 0, but it should not have!"):
            test_tile.tileno = -1

    def test_l1_attributes_bytes(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_tile',
                                     'test_attributes_bytes'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_tile = tekton_tile.TektonTile()
            test_tile.tileno = test_case["tileno"]
            test_tile.bts_type = test_case["bts_type"]
            test_tile.h_mirror = test_case["h"]
            test_tile.v_mirror = test_case["v"]
            expected_result = int_list_to_bytes(test_case["expected_result"])
            self.assertEqual(test_tile.l1_attributes_bytes,
                             expected_result,
                             "TektonTile l1_attributes_bytes did not match expected result.")

    def test_bts_number_byte(self):
        test_tile = tekton_tile.TektonTile()
        test_tile.bts_num = 0x7e
        expected_result = (0x7e).to_bytes(1, byteorder="big")
        self.assertEqual(expected_result, test_tile.bts_number_byte,
                         "TektonTile BTS Number Byte did not match expected result.")

    def test_copy(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_tile',
                                     'test_copy'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_tile_source = tekton_tile.TektonTile()
            test_tile_source.tileno = test_item["tileno"]
            test_tile_source.bts_type = test_item["bts_type"]
            test_tile_source.bts_num = test_item["bts_num"]
            test_tile_source.h_mirror = test_item["h_mirror"]
            test_tile_source.v_mirror = test_item["v_mirror"]
            test_tile_copy = test_tile_source.copy()

            self.assertNotEqual(id(test_tile_source), id(test_tile_copy), "TektonTile copy did not create a unique object.")
            self.assertEqual(test_tile_source, test_tile_copy, "Copied Tekton Tile object not equal to source.")

    def _populate_bin_op_operands(self, test_item):
        test_tile_left = tekton_tile.TektonTile()
        test_tile_right = tekton_tile.TektonTile()
        test_tile_left.tileno = test_item["left"]["tileno"]
        test_tile_left.bts_type = test_item["left"]["bts_type"]
        test_tile_left.bts_num = test_item["left"]["bts_num"]
        test_tile_left.h_mirror = test_item["left"]["h_mirror"]
        test_tile_left.v_mirror = test_item["left"]["v_mirror"]
        test_tile_right.tileno = test_item["right"]["tileno"]
        test_tile_right.bts_type = test_item["right"]["bts_type"]
        test_tile_right.bts_num = test_item["right"]["bts_num"]
        test_tile_right.h_mirror = test_item["right"]["h_mirror"]
        test_tile_right.v_mirror = test_item["right"]["v_mirror"]

        return test_tile_left, test_tile_right