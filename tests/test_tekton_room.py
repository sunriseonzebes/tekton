from testing_common import tekton, load_test_data_dir, int_list_to_bytes, load_room_from_test_data
from tekton import tekton_room, tekton_tile, tekton_tile_grid, tekton_room_header_data, tekton_room_state
import os
import unittest

class TestTektonRoom(unittest.TestCase):
    def test_init(self):
        test_room = tekton_room.TektonRoom()
        self.assertTrue(isinstance(test_room, tekton_room.TektonRoom), msg="Tekton Room did not instantiate correctly!")
        self.assertIsNone(test_room.name)
        self.assertEqual(0x00, test_room._header, "Tekton Room default header address is not 0x00!")
        self.assertEqual(test_room.width_screens, 1)
        self.assertEqual(test_room.height_screens, 1)
        self.assertTrue(isinstance(test_room.standard_state, tekton_room_state.TektonRoomState),
                        msg="TektonRoom.standard_state did not initialize correctly!")
        self.assertEqual([], test_room.extra_states, "TektonRoom.standard_state did not initialize correctly!")
        self.assertTrue(isinstance(test_room.header_data, tekton_room_header_data.TektonRoomHeaderData))
        self.assertEqual(test_room.level_data_length, 0)
        self.assertEqual(test_room.doors, [], "Tekton Room doors list did not initialize correctly!")
        self.assertTrue(test_room.write_level_data, msg="Tekton Room write_level_data did not initialize correctly!")

        test_room = None
        test_room = tekton_room.TektonRoom(3, 4)
        self.assertTrue(isinstance(test_room, tekton_room.TektonRoom), msg="Tekton Room did not instantiate correctly!")
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

    def test_compressed_level_data(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_room',
                                     'test_compressed_level_data'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_room = load_room_from_test_data(test_item)
            if "standard_state" in test_item.keys():
                expected_result = int_list_to_bytes(test_item["standard_state"]["expected_result"])
                actual_result = test_room.compressed_level_data(test_room.standard_state)
                self.assertEqual(expected_result, actual_result, "TektonRoom did not produce correct compressed data!")
            if "extra_states" in test_item.keys():
                for i in range(len(test_item["extra_states"])):
                    expected_result = int_list_to_bytes(test_item["extra_states"][i]["room_state"]["expected_result"])
                    actual_result = test_room.compressed_level_data(test_room.extra_states[i].room_state)
                    self.assertEqual(expected_result, actual_result,
                                     "TektonRoom did not produce correct compressed data!")

        test_room = tekton_room.TektonRoom()
        test_room.level_data_length = 3
        test_room.standard_state.tiles = tekton_tile_grid.TektonTileGrid(16, 16)
        test_room.standard_state.tiles.fill()

        with self.assertRaises(tekton_room.CompressedDataTooLargeError):
            actual_result = test_room.compressed_level_data(test_room.standard_state)

