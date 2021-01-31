from testing_common import tekton, load_test_data_dir, int_list_to_bytes, load_room_from_test_tiles
from tekton import tekton_compressor, tekton_tile, tekton_field
import os
import unittest

class TestTektonCompressionMapper(unittest.TestCase):
    def test_init(self):
        test_mapper = tekton_compressor.TektonCompressionMapper()
        self.assertTrue(isinstance(test_mapper, tekton_compressor.TektonCompressionMapper))
        self.assertEqual(b'',
                         test_mapper.uncompressed_data,
                         "TektonCompressionMapper uncompressed_data did not init with correct value!")
        self.assertEqual([],
                         test_mapper._byte_map,
                         "TektonCompressionMapper _byte_map did not init with correct value!")

    def test_generate_compression_fields(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'integration',
                                     'test_tekton_compressor',
                                     'test_generate_compression_fields'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_mapper = tekton_compressor.TektonCompressionMapper()
            test_room = load_room_from_test_tiles(test_case)
            test_mapper.uncompressed_data = test_room.tiles.uncompressed_data
            test_mapper._init_byte_map()
            test_mapper._map_fields()
            actual_result = test_mapper._generate_compression_fields()
            self.assertEqual(len(test_case["expected_results"]),
                             len(actual_result),
                             "Compression Mapper compress_first_pass yielded the wrong number of compression fields!")
            for field_num in range(len(test_case["expected_results"])):
                expected_field = test_case["expected_results"][field_num]
                actual_field = actual_result[field_num]
                expected_type = self._get_expected_type(expected_field["type"])
                self.assertTrue(isinstance(actual_field, expected_type))

    def test_map_repeating_bytes_fields(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_map_repeating_bytes_fields'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_mapper = tekton_compressor.TektonCompressionMapper()
            test_mapper.uncompressed_data = int_list_to_bytes(test_case["uncompressed_data"])
            test_mapper._init_byte_map()
            test_mapper._map_repeating_byte_fields()
            for result in test_case["expected_results"]:
                start_index = result["start_index"]
                end_index = result["end_index"]
                expected_field = result["field"]
                expected_type = self._get_expected_type(expected_field["type"])
                actual_field = test_mapper._byte_map[start_index]
                self.assertTrue(isinstance(actual_field, expected_type))
                if isinstance(actual_field, tekton_field.TektonByteFillField):
                    self.assertEqual(expected_field["byte"].to_bytes(1, byteorder="big"),
                                     actual_field.byte,
                                     "map_repeating_bytes_fields yielded incorrect byte value at index {}!".format(start_index))
                    self.assertEqual(expected_field["num_bytes"],
                                     actual_field.num_bytes,
                                     "map_repeating_bytes_fields yielded incorrect num_bytes value at index {}!".format(start_index))
                for i in range(start_index, end_index+1):
                    error_message = "map_repeating_bytes_fields did not map fields correctly! " \
                                    "Object at index {} should match object at index {}"
                    self.assertEqual(actual_field,
                                     test_mapper._byte_map[i],
                                     error_message.format(i, start_index))


    def _get_expected_type(self, type_string):
        if type_string == "TektonByteFillField":
            return tekton_field.TektonByteFillField
        if type_string == "NoneType":
            return type(None)
        else:
            raise ValueError("Type string {} not understood!".format(type_string))






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
            test_room = load_room_from_test_tiles(test_item)
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
            test_room = load_room_from_test_tiles(test_item)
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
            test_room = load_room_from_test_tiles(test_item)
            actual_result = tekton_compressor.compress_level_data(test_room.tiles, test_item["level_data_length"])
            self.assertEqual(expected_result, actual_result, "Room data did not compress correctly.")
