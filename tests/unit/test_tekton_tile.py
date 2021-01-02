from testing_common import tekton
from tekton import tekton_tile
import unittest

class TestTektonTile(unittest.TestCase):
    def test_init(self):
        test_tile = tekton_tile.TektonTile()
        self.assertNotEqual(test_tile, None, "Test Tile is None!")
        self.assertEqual(test_tile.bts, 0x00, "Test Tile BTS is not 0x00.")
        self.assertEqual(test_tile.tileno, 0x00, "Test Tile Tile number is not 0x00.")
        self.assertFalse(test_tile.h_mirror, "Test Tile Horizontal Mirror is not False.")
        self.assertFalse(test_tile.v_mirror, "Test Tile Vertical Mirror is not False.")

    def test_repr(self):
        test_tile = tekton_tile.TektonTile()

        test_result = test_tile.__repr__()
        expected_result = "TektonTile:\nTile Number: 0\nBTS: 0\nTile Horizontal Mirror: False\nTile Vertical Mirror: False"

        self.assertEqual(test_result, expected_result, "Tekton Tile repr function incorrect!")

    def test_eq(self):
        test_data = [
            {
                "left":
                     {"tileno": 0, "bts": 0, "h_mirror": False, "v_mirror": False},
                "right":
                    {"tileno": 0, "bts": 0, "h_mirror": False, "v_mirror": False}
            },
            {
                "left":
                    {"tileno": 15, "bts": 3, "h_mirror": True, "v_mirror": False},
                "right":
                    {"tileno": 15, "bts": 3, "h_mirror": True, "v_mirror": False}
            },
            {
                "left":
                    {"tileno": 31, "bts": 8, "h_mirror": False, "v_mirror": True},
                "right":
                    {"tileno": 31, "bts": 8, "h_mirror": False, "v_mirror": True}
            }
        ]

        for test_item in test_data:
            test_tile_left, test_tile_right = self._populate_bin_op_operands(test_item)
            self.assertEqual(test_tile_left, test_tile_right)

    def test_ne(self):
        test_data = [
            {
                "left":
                    {"tileno": 10, "bts": 0, "h_mirror": False, "v_mirror": False},
                "right":
                    {"tileno": 0, "bts": 0, "h_mirror": False, "v_mirror": False}
            },
            {
                "left":
                    {"tileno": 6, "bts": 4, "h_mirror": False, "v_mirror": True},
                "right":
                    {"tileno": 6, "bts": 5, "h_mirror": False, "v_mirror": True}
            },
            {
                "left":
                    {"tileno": 11, "bts": 8, "h_mirror": False, "v_mirror": True},
                "right":
                    {"tileno": 11, "bts": 8, "h_mirror": True, "v_mirror": True}
            }
        ]

        for test_item in test_data:
            test_tile_left, test_tile_right = self._populate_bin_op_operands(test_item)
            self.assertNotEqual(test_tile_left, test_tile_right)

        test_tile = tekton_tile.TektonTile()
        self.assertNotEqual(test_tile, "Test string")

    def test_bts_byte(self):
        test_data = [
            {"bts": 8, "h": False, "v": False, "result": (0b10000001).to_bytes(1, byteorder="big")},
            {"bts": 2, "h": False, "v": False, "result": (0b00100001).to_bytes(1, byteorder="big")},
            {"bts": 8, "h": True, "v": False, "result": (0b10000101).to_bytes(1, byteorder="big")},
            {"bts": 4, "h": False, "v": True, "result": (0b01001001).to_bytes(1, byteorder="big")},
            {"bts": 5, "h": True, "v": True, "result": (0b01011101).to_bytes(1, byteorder="big")}
        ]

        for test_case in test_data:
            test_tile = tekton_tile.TektonTile()
            test_tile.bts = test_case["bts"]
            test_tile.h_mirror = test_case["h"]
            test_tile.v_mirror = test_case["v"]
            expected_result = test_case["result"]
            self.assertEqual(test_tile.bts_tile_mirror_byte, expected_result, "Test Tile BTS Byte did not match expected result.")

    def test_tileno_byte(self):
        test_tile = tekton_tile.TektonTile()
        test_tile.tileno = 10
        expected_result = (10).to_bytes(1, byteorder="big")
        self.assertEqual(test_tile.tile_byte, expected_result, "Test Tile Tile Byte did not match expected result.")

    def test_copy(self):
        test_tile_source = tekton_tile.TektonTile()
        test_tile_copy = test_tile_source.copy()
        self.assertNotEqual(id(test_tile_source), id(test_tile_copy), "TektonTile copy did not create a unique object.")
        self.assertEqual(test_tile_source, test_tile_copy, "Copied Tekton Tile object not equal to source.")

    def _populate_bin_op_operands(self, test_item):
        test_tile_left = tekton_tile.TektonTile()
        test_tile_right = tekton_tile.TektonTile()
        test_tile_left.tileno = test_item["left"]["tileno"]
        test_tile_left.bts = test_item["left"]["bts"]
        test_tile_left.h_mirror = test_item["left"]["h_mirror"]
        test_tile_left.v_mirror = test_item["left"]["v_mirror"]
        test_tile_right.tileno = test_item["right"]["tileno"]
        test_tile_right.bts = test_item["right"]["bts"]
        test_tile_right.h_mirror = test_item["right"]["h_mirror"]
        test_tile_right.v_mirror = test_item["right"]["v_mirror"]

        return test_tile_left, test_tile_right