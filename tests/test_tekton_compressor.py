from testing_common import tekton, load_test_data_dir, int_list_to_bytes
from tekton import tekton_compressor, tekton_tile, tekton_room
import os
import unittest


class TestTektonCompressor(unittest.TestCase):
    def test_find_layer_1_fields_for_compression(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_find_layer_1_fields_for_compression'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            expected_result = test_item["expected_result"]
            test_room = self._load_room_from_test_tiles(test_item)
            actual_result = tekton_compressor._find_layer_1_fields_for_compression(test_room.tiles)
            self.assertEqual(expected_result, actual_result, "Compressor did not find the correct layer 1 fields.")

    def test_find_bts_layer_fields_for_compression(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_find_bts_layer_fields_for_compression'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            expected_result = test_item["expected_result"]
            test_room = self._load_room_from_test_tiles(test_item)
            actual_result = tekton_compressor._find_bts_layer_fields_for_compression(test_room.tiles)
            for i in range(len(expected_result)):
                self.assertTrue(isinstance(actual_result[i], type(expected_result[i])),
                                msg="Field at index {index} should be type {expected_type} but it is type {actual_type}".format(
                                    index=i, expected_type=type(expected_result[i]), actual_type=type(actual_result[i])
                                ))
            self.assertEqual(expected_result, actual_result, "Compressor did not find the correct bts layer fields.")

    def test_tiles_layer_1_equivalent(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_tiles_layer_1_equivalent'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            if test_item["expected_result"] == True:
                self.assertTrue(tekton_compressor._tiles_layer_1_equivalent(test_item["left"], test_item["right"]))
            else:
                self.assertFalse(tekton_compressor._tiles_layer_1_equivalent(test_item["left"], test_item["right"]))

        with self.assertRaises(TypeError):
            tekton_compressor._tiles_layer_1_equivalent("A string", tekton_tile.TektonTile())
        with self.assertRaises(TypeError):
            tekton_compressor._tiles_layer_1_equivalent(tekton_tile.TektonTile(), "A string")

    def test_tiles_bts_layer_equivalent(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_tiles_bts_layer_equivalent'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            if test_item["expected_result"] == True:
                self.assertTrue(tekton_compressor._tiles_bts_layer_equivalent(test_item["left"], test_item["right"]))
            else:
                self.assertFalse(tekton_compressor._tiles_bts_layer_equivalent(test_item["left"], test_item["right"]))

        with self.assertRaises(TypeError):
            tekton_compressor._tiles_layer_1_equivalent("A string", tekton_tile.TektonTile())
        with self.assertRaises(TypeError):
            tekton_compressor._tiles_layer_1_equivalent(tekton_tile.TektonTile(), "A string")

    def test_generate_compressed_level_data_header(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_generate_compressed_level_data_header'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            expected_result = int_list_to_bytes(test_item["expected_result"])
            actual_result = tekton_compressor._generate_compressed_level_data_header(test_item["room_width_screens"],
                                                                                     test_item["room_height_screens"])
            self.assertEqual(expected_result, actual_result, "Level data header did not generate correct output!")

    def test_compress_level_data(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'sample_compression_data'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            expected_result = int_list_to_bytes(test_item["expected_result"])
            test_room = self._load_room_from_test_tiles(test_item)
            actual_result = tekton_compressor.compress_level_data(test_room.tiles, test_item["level_data_length"])
            self.assertEqual(expected_result, actual_result, "Room data did not compress correctly.")

    def _load_room_from_test_tiles(self, test_tile_data):
        test_room = tekton_room.TektonRoom(test_tile_data["room_width"], test_tile_data["room_height"])
        tiles_width = test_room.tiles.width
        if "level_data_length" in test_tile_data.keys():
            test_room.level_data_length = test_tile_data["level_data_length"]
        counter = 0
        for tile_group in test_tile_data["test_tiles"]:
            for i in range(tile_group["count"]):
                for key in tile_group["tile"].keys():
                    setattr(test_room.tiles[counter % tiles_width][counter // tiles_width],
                            key,
                            tile_group["tile"][key])
                counter += 1

        return test_room
