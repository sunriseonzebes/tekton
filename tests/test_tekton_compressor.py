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
        self.assertEqual(1,
                         test_mapper._width_screens,
                         "TektonCompressionMapper _width_screens did not init with correct value!")
        self.assertEqual(1,
                         test_mapper._height_screens,
                         "TektonCompressionMapper _height_screens did not init with correct value!")

    def test_width_screens(self):
        test_mapper = tekton_compressor.TektonCompressionMapper()
        test_mapper.width_screens = 4
        self.assertEqual(4,
                         test_mapper.width_screens,
                         "TektonCompressionMapper did not return correct width_screens value.")
        with self.assertRaises(ValueError):
            test_mapper.width_screens = 0
        with self.assertRaises(ValueError):
            test_mapper.width_screens = 51
        with self.assertRaises(ValueError):
            test_mapper._height_screens = 10
            test_mapper.width_screens = 6
        with self.assertRaises(TypeError):
            test_mapper.width_screens = "A string."

    def test_height_screens(self):
        test_mapper = tekton_compressor.TektonCompressionMapper()
        test_mapper.height_screens = 4
        self.assertEqual(4,
                         test_mapper.height_screens,
                         "TektonCompressionMapper did not return correct width_screens value.")
        with self.assertRaises(ValueError):
            test_mapper.height_screens = 0
        with self.assertRaises(ValueError):
            test_mapper.height_screens = 51
        with self.assertRaises(ValueError):
            test_mapper._width_screens = 8
            test_mapper.height_screens = 8
        with self.assertRaises(TypeError):
            test_mapper.height_screens = "A string."

    def test_map_fields(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'integration',
                                     'test_tekton_compressor',
                                     'test_map_fields'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_mapper = tekton_compressor.TektonCompressionMapper()
            test_room = load_room_from_test_tiles(test_case)
            test_mapper.uncompressed_data = test_room.standard_state.tiles.uncompressed_data
            test_mapper._init_byte_map()
            test_mapper._map_fields()
            for expected_map_range in test_case["expected_results"]:
                actual_field = test_mapper._byte_map[expected_map_range["start_index"]]
                expected_type = self._get_expected_type(expected_map_range["type"])
                self.assertTrue(isinstance(actual_field, expected_type),
                                msg="Byte Map index {} should be {} but is {}!".format(expected_map_range["start_index"],
                                                                              expected_type,
                                                                              type(actual_field)))

                if isinstance(actual_field, tekton_field.TektonWordFillField):
                    self.assertEqual(int_list_to_bytes(expected_map_range["word"]),
                                     actual_field.word,
                                     "Incorrect byte map word at index {}!".format(expected_map_range["start_index"]))
                    self.assertEqual(expected_map_range["num_bytes"],
                                     actual_field.num_bytes,
                                     "Incorrect byte map num_bytes at index {}!".format(expected_map_range["start_index"]))
                if isinstance(actual_field, tekton_field.TektonByteFillField):
                    self.assertEqual(expected_map_range["byte"].to_bytes(1, byteorder="big"),
                                     actual_field.byte,
                                     "Incorrect byte map byte at index {}!".format(expected_map_range["start_index"]))
                    self.assertEqual(expected_map_range["num_bytes"],
                                     actual_field.num_bytes,
                                     "Incorrect byte map num_bytes at index {}!".format(expected_map_range["start_index"]))
                if isinstance(actual_field, tekton_field.TektonDirectCopyField):
                    self.assertEqual(int_list_to_bytes(expected_map_range["bytes_data"]),
                                     actual_field.bytes_data,
                                     "Incorrect byte map bytes_data at index {}!".format(expected_map_range["start_index"]))
                for i in range(expected_map_range["start_index"], expected_map_range["end_index"]):
                    self.assertEqual(actual_field,
                                     test_mapper._byte_map[i],
                                     "Incorrect field at byte map index {}!".format(i))

    def test_compressed_level_data_header(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_compressed_level_data_header'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_mapper = tekton_compressor.TektonCompressionMapper()
            test_mapper.width_screens = test_case["room_width_screens"]
            test_mapper.height_screens = test_case["room_height_screens"]
            expected_result = int_list_to_bytes(test_case["expected_result"])
            actual_result = test_mapper.compressed_level_data_header
            self.assertEqual(expected_result, actual_result, "Level data header did not generate correct output!")


    def test_compressed_data(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'integration',
                                     'test_tekton_compressor',
                                     'test_compressed_data'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_mapper = tekton_compressor.TektonCompressionMapper()
            test_room = load_room_from_test_tiles(test_item)
            test_mapper.width_screens = test_room.width_screens
            test_mapper.height_screens = test_room.height_screens
            test_mapper.uncompressed_data = test_room.standard_state.tiles.uncompressed_data
            expected_result = int_list_to_bytes(test_item["expected_result"])
            actual_result = test_mapper.compressed_data
            self.assertEqual(expected_result, actual_result, "Room data did not compress correctly.")


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
            test_mapper.uncompressed_data = test_room.standard_state.tiles.uncompressed_data
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
                self.assertTrue(isinstance(actual_field, expected_type),
                                msg="Field {} should be {} but is {}!".format(field_num,
                                                                                  expected_type,
                                                                                  type(actual_field)))
                if isinstance(actual_field, tekton_field.TektonDirectCopyField):
                    expected_bytes_data = int_list_to_bytes(expected_field["bytes_data"])
                    self.assertEqual(expected_bytes_data,
                                     actual_field.bytes_data,
                                     "Field {} does not have correct bytes data!".format(field_num))
                if isinstance(actual_field, tekton_field.TektonByteFillField):
                    self.assertEqual(expected_field["num_bytes"],
                                     actual_field.num_bytes,
                                     "Field {} does not have correct num_bytes data!".format(field_num))
                    self.assertEqual(expected_field["byte"].to_bytes(1, byteorder="big"),
                                     actual_field.byte,
                                     "Field {} does not have correct byte data!".format(field_num))

    def test_map_repeating_word_fields(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_map_repeating_word_fields'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_mapper = tekton_compressor.TektonCompressionMapper()
            test_mapper.uncompressed_data = int_list_to_bytes(test_case["uncompressed_data"])
            test_mapper._init_byte_map()
            test_mapper._map_repeating_word_fields()
            for result in test_case["expected_results"]:
                start_index = result["start_index"]
                end_index = result["end_index"]
                expected_field = result["field"]
                expected_type = self._get_expected_type(expected_field["type"])
                actual_field = test_mapper._byte_map[start_index]
                self.assertTrue(isinstance(actual_field, expected_type),
                                msg="Field at index {} should be {} but it is {}!".format(start_index, expected_type, type(actual_field)))
                if isinstance(actual_field, tekton_field.TektonWordFillField):
                    self.assertEqual(int_list_to_bytes(expected_field["word"]),
                                     actual_field.word,
                                     "map_repeating_word_fields yielded incorrect word value at index {}!".format(
                                         start_index))
                    self.assertEqual(expected_field["num_bytes"],
                                     actual_field.num_bytes,
                                     "map_repeating_word_fields yielded incorrect num_bytes value at index {}!".format(
                                         start_index))
                for i in range(start_index, end_index + 1):
                    error_message = "map_repeating_word_fields did not map fields correctly! " \
                                    "Object at index {} should match object at index {}"
                    self.assertEqual(actual_field,
                                     test_mapper._byte_map[i],
                                     error_message.format(i, start_index))


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

    def test_map_direct_copy_fields(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_map_direct_copy_fields'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_mapper = tekton_compressor.TektonCompressionMapper()
            test_mapper.uncompressed_data = int_list_to_bytes(test_case["uncompressed_data"])
            test_mapper._init_byte_map()
            if "test_fills" in test_case.keys():
                test_fill_field = tekton_field.TektonField()
                for test_fill in test_case["test_fills"]:
                    for i in range(test_fill["start_index"], test_fill["end_index"]+1):
                        test_mapper._byte_map[i] = test_fill_field
            test_mapper._map_direct_copy_fields()
            for result in test_case["expected_results"]:
                start_index = result["start_index"]
                end_index = result["end_index"]
                expected_field = result["field"]
                expected_type = self._get_expected_type(expected_field["type"])
                actual_field = test_mapper._byte_map[start_index]
                self.assertTrue(isinstance(actual_field, expected_type))
                if isinstance(actual_field, tekton_field.TektonDirectCopyField):
                    self.assertEqual(int_list_to_bytes(expected_field["bytes_data"]),
                                     actual_field.bytes_data,
                                     "map_direct_copy_fields yielded incorrect bytes_data value at index {}!".format(start_index))
                for i in range(start_index, end_index+1):
                    error_message = "map_direct_copy_fields did not map fields correctly! " \
                                    "Object at index {} should match object at index {}"
                    self.assertEqual(actual_field,
                                     test_mapper._byte_map[i],
                                     error_message.format(i, start_index))

    def _get_expected_type(self, type_string):
        if type_string == "TektonWordFillField":
            return tekton_field.TektonWordFillField
        if type_string == "TektonByteFillField":
            return tekton_field.TektonByteFillField
        if type_string == "TektonDirectCopyField":
            return tekton_field.TektonDirectCopyField
        if type_string == "NoneType":
            return type(None)
        else:
            raise ValueError("Type string {} not understood!".format(type_string))
