from testing_common import tekton, load_test_data_dir, int_list_to_bytes
from tekton import tekton_compressor, tekton_tile, tekton_room
import os
import unittest


class TestTektonCompressor(unittest.TestCase):
    def test_find_blocks_for_compression(self):
        test_room = tekton_room.TektonRoom()

        for i in range(14):
            test_room.tiles[i][0].tileno = 10
            test_room.tiles[i][0].bts_type = 8

        first_field = tekton_compressor.L1RepeaterField()
        first_field.num_reps = 14
        first_field.tileno = 10
        first_field.bts_type = 8
        last_field = tekton_compressor.L1RepeaterField()
        last_field.num_reps = 242
        last_field.tileno = 0
        last_field.bts_type = 0

        test_result = tekton_compressor._find_blocks_for_compression(test_room.tiles)
        expected_result = [first_field, last_field]

        self.assertEqual(test_result, expected_result, "Compressor did not find the correct blocks.")

    def test_generate_compressed_level_data_header(self):
        expected_result = b'\x01\x00\x02'
        test_result = tekton_compressor._generate_compressed_level_data_header()

        self.assertEqual(expected_result, test_result)

    def test_compress_level_data(self):
        test_room = tekton_room.TektonRoom()
        test_room.level_data_length = 155
        test_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                      'fixtures',
                                      'unit',
                                      'sample_compression_data',
                                      'generic_blank_room.bin'
                                      )
        with open(test_file_path, "rb") as f:
            expected_result = f.read()
        test_result = tekton_compressor.compress_level_data(test_room.tiles)
        self.assertEqual(expected_result, test_result, "Room data did not compress correctly.")

        test_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                      'fixtures',
                                      'unit',
                                      'sample_compression_data',
                                      'generic_blank_room_padded.bin'
                                      )
        with open(test_file_path, "rb") as f:
            expected_result = f.read()
        test_result = tekton_compressor.compress_level_data(test_room.tiles, test_room.level_data_length)
        self.assertEqual(expected_result, test_result, "Room data did not compress correctly.")


class TestL1RepeaterField(unittest.TestCase):
    def test_init(self):
        test_field = tekton_compressor.L1RepeaterField()
        self.assertTrue(isinstance(test_field, tekton_compressor.L1RepeaterField))
        self.assertEqual(0, test_field.num_reps, "L1RepeaterField num_reps did not initialize to 0!")
        self.assertEqual(0x00, test_field.bts_type, "L1RepeaterField bts_type did not initialize to 0!")
        self.assertEqual(0x00, test_field.tileno, "L1RepeaterField tileno did not initialize to 0!")
        self.assertFalse(test_field.h_mirror, msg="L1RepeaterField h_mirror did not initialize to False!")
        self.assertFalse(test_field.v_mirror, msg="L1RepeaterField v_mirror did not initialize to False!")

    def test_eq(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_l1_repeater_field',
                                     'test_eq'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field_left, test_field_right = self._get_fields_from_eq_test_data(test_item)
            self.assertEqual(test_field_left, test_field_right)

    def test_ne(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_l1_repeater_field',
                                     'test_ne'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field_left, test_field_right = self._get_fields_from_eq_test_data(test_item)
            self.assertNotEqual(test_field_left, test_field_right)

    def test_bts_byte(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_l1_repeater_field',
                                     'test_bts_byte'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_field = tekton_compressor.L1RepeaterField()
            test_field.bts_type = test_case["bts_type"]
            test_field.h_mirror = test_case["h"]
            test_field.v_mirror = test_case["v"]
            expected_result = int_list_to_bytes(test_case["expected_result"])
            self.assertEqual(test_field.bts_tile_mirror_byte,
                             expected_result,
                             "L1RepeaterField BTS Byte did not match expected result.")

    def test_tileno_byte(self):
        test_field = tekton_compressor.L1RepeaterField()
        test_field.tileno = 10
        expected_result = (10).to_bytes(1, byteorder="big")
        self.assertEqual(test_field.tile_byte, expected_result, "L1RepeaterField Tile Byte did not match expected result.")


    def test_compressed_data(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_l1_repeater_field',
                                     'test_compressed_data'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field = tekton_compressor.L1RepeaterField()
            test_field.tileno = test_item["tileno"]
            test_field.bts_type = test_item["bts"]
            test_field.h_mirror = test_item['h_mirror']
            test_field.v_mirror = test_item['v_mirror']
            test_field.num_reps = test_item["num_reps"]

            test_result = test_field.compressed_data
            expected_result = int_list_to_bytes(test_item["expected_result"])
            self.assertEqual(test_result, expected_result, "Error when compressing repeater block {}".format(test_item))


    def _get_fields_from_eq_test_data(self, test_item):
        test_field_left = tekton_compressor.L1RepeaterField()
        test_field_right = tekton_compressor.L1RepeaterField()

        test_field_left.tileno = test_item["left"]["tileno"]
        test_field_left.bts_type = test_item["left"]["bts"]
        test_field_left.h_mirror = test_item["left"]["h_mirror"]
        test_field_left.v_mirror = test_item["left"]["v_mirror"]
        test_field_left.num_reps = test_item["left"]["num_reps"]

        test_field_right.tileno = test_item["right"]["tileno"]
        test_field_right.bts_type = test_item["right"]["bts"]
        test_field_right.h_mirror = test_item["right"]["h_mirror"]
        test_field_right.v_mirror = test_item["right"]["v_mirror"]
        test_field_right.num_reps = test_item["right"]["num_reps"]

        return test_field_left, test_field_right
