from testing_common import tekton, load_test_data_dir, int_list_to_bytes
from tekton import tekton_room, tekton_tile, tekton_tile_grid
import os
import unittest

class TestTektonRoom(unittest.TestCase):
    def test_init(self):
        test_room = tekton_room.TektonRoom()
        self.assertTrue(isinstance(test_room, tekton_room.TektonRoom), msg="Tekton Room did not instantiate correctly!")
        self.assertIsNone(test_room.name)
        self.assertEqual(0x00, test_room._header, "Tekton Room default header address is not 0x00!")
        self.assertEqual(test_room.tiles.width, 16, "Test Room has incorrect number of columns!")
        for x in range(16):
            self.assertEqual(len(test_room.tiles[x]), 16, "Test Room has incorrect number of rows!")
            for y in range(16):
                self.assertTrue(isinstance(test_room.tiles[x][y], tekton_tile.TektonTile), "Test Room tile at {0}, {1} is not a TektonTile".format(x, y))
        self.assertEqual(test_room.width_screens, 1)
        self.assertEqual(test_room.height_screens, 1)
        self.assertEqual(0x00, test_room._level_data_address, "Tekton Room default level data address is not 0x00!")
        self.assertEqual(test_room.level_data_length, 0)
        self.assertEqual(test_room.doors, [], "Tekton Room doors list did not initialize correctly!")

        test_room = None
        test_room = tekton_room.TektonRoom(3, 4)
        self.assertTrue(isinstance(test_room, tekton_room.TektonRoom), msg="Tekton Room did not instantiate correctly!")
        self.assertEqual(test_room.tiles.width, 48, "Test Room has incorrect number of columns!")
        for x in range(16):
            self.assertEqual(len(test_room.tiles[x]), 64, "Test Room has incorrect number of rows!")
            for y in range(16):
                self.assertTrue(isinstance(test_room.tiles[x][y], tekton_tile.TektonTile),
                                "Test Room tile at {0}, {1} is not a TektonTile".format(x, y))
        self.assertEqual(test_room.width_screens, 3)
        self.assertEqual(test_room.height_screens, 4)

    def test_room_header(self):
        test_room = tekton_room.TektonRoom()

        test_room.header = 0x795d4
        self.assertEqual(0x795d4, test_room.header)

        with self.assertRaises(TypeError):
            test_room.header = "795d4"
        with self.assertRaises(ValueError):
            test_room.header = -5

    def test_level_data_address(self):
        test_room = tekton_room.TektonRoom()

        test_room.level_data_address = 0x21bcd2
        self.assertEqual(0x21bcd2, test_room.level_data_address, "Tekton Room does not have correct level data address")

        with self.assertRaises(TypeError):
            test_room.level_data_address = "21bcd2"
        with self.assertRaises(ValueError):
            test_room.level_data_address = -5

    def test_compressed_level_data(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_room',
                                     'test_compressed_level_data'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            expected_result = int_list_to_bytes(test_item["expected_result"])
            test_room = tekton_room.TektonRoom()
            test_room.level_data_length = 155
            actual_result = test_room.compressed_level_data()
            self.assertEqual(expected_result, actual_result, "TektonRoom did not produce correct compressed data!")

        test_room = tekton_room.TektonRoom()
        test_room.level_data_length = 3

        with self.assertRaises(tekton_room.CompressedDataTooLargeError):
            actual_result = test_room.compressed_level_data()

