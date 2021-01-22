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




class TestL1RepeaterField(unittest.TestCase):
    def test_init(self):
        test_field = tekton_compressor.L1RepeaterField()
        self.assertTrue(isinstance(test_field, tekton_compressor.L1RepeaterField))
        self.assertEqual(0, test_field.num_reps, "L1RepeaterField num_reps did not initialize to 0!")
        self.assertEqual(0x00, test_field.bts_type, "L1RepeaterField bts_type did not initialize to 0!")
        self.assertFalse(test_field.h_mirror, msg="L1RepeaterField h_mirror did not initialize to False!")
        self.assertFalse(test_field.v_mirror, msg="L1RepeaterField v_mirror did not initialize to False!")
        self.assertEqual(0x00, test_field._tileno, "L1RepeaterField _tileno did not initialize to 0!")

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
            self.assertEqual(test_field_left,
                             test_field_right,
                             "L1RepeaterField objects should be equal but they're not!")

        test_field = tekton_compressor.L1RepeaterField()
        with self.assertRaises(TypeError):
            test_field == "A string"

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
            self.assertNotEqual(test_field_left,
                                test_field_right,
                                "L1RepeaterField objects are equal but they shouldn't be!")

        test_field = tekton_compressor.L1RepeaterField()
        with self.assertRaises(TypeError):
            test_field != "A string"

    def test_tileno(self):
        test_field = tekton_compressor.L1RepeaterField()
        test_field.tileno = 0x10a
        expected_result = 0x10a
        self.assertEqual(expected_result,
                         test_field.tileno,
                         "L1RepeaterField.tileno did not return the correct result!")

        with self.assertRaises(TypeError,
                               msg="L1RepeaterField tileno should only accept int, but it accepted string!"):
            test_field.tileno = "rock"
        with self.assertRaises(ValueError,
                               msg="L1RepeaterField tileno should not accept negative numbers, but it did!"):
            test_field.tileno = -1
        with self.assertRaises(ValueError,
                               msg="L1RepeaterField tileno should not accept numbers greater than 0x3ff, but it did!"):
            test_field.tileno = 0x400

    def test_field_header_and_reps_bytes(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_l1_repeater_field',
                                     'test_field_header_and_reps_bytes'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field = tekton_compressor.L1RepeaterField()
            test_field.num_reps = test_item["num_reps"]
            expected_result = int_list_to_bytes(test_item["expected_result"])
            actual_result = test_field.field_header_and_reps_bytes
            self.assertEqual(expected_result,
                             actual_result,
                             "L1RepeaterField did not return correct field_header_and_reps bytes!")

    def test_attributes_bytes(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_l1_repeater_field',
                                     'test_attributes_bytes'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_field = tekton_compressor.L1RepeaterField()
            test_field.tileno = test_case["tileno"]
            test_field.bts_type = test_case["bts_type"]
            test_field.h_mirror = test_case["h"]
            test_field.v_mirror = test_case["v"]
            expected_result = int_list_to_bytes(test_case["expected_result"])
            self.assertEqual(test_field.attributes_bytes,
                             expected_result,
                             "L1RepeaterField attributes_bytes did not match expected result.")

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
            self.assertEqual(expected_result, test_result, "Error when compressing L1RepeaterField{}".format(test_item))

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


class TestBTSNumRepeaterField(unittest.TestCase):
    def test_init(self):
        test_field = tekton_compressor.BTSNumRepeaterField()
        self.assertTrue(isinstance(test_field, tekton_compressor.BTSNumRepeaterField))
        self.assertEqual(0, test_field.num_reps, "BTSNumRepeaterField num_reps did not initialize to 0!")
        self.assertEqual(0x00, test_field.bts_num, "BTSNumRepeaterField bts_type did not initialize to 0!")

    def test_eq(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_bts_num_repeater_field',
                                     'test_eq'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field_left, test_field_right = self._get_fields_from_eq_test_data(test_item)
            self.assertEqual(test_field_left,
                             test_field_right,
                             "BTSNumRepeaterField objects should be equal but they're not!")

        test_field = tekton_compressor.BTSNumRepeaterField()
        with self.assertRaises(TypeError):
            test_field == "A string"

    def test_ne(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_bts_num_repeater_field',
                                     'test_ne'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field_left, test_field_right = self._get_fields_from_eq_test_data(test_item)
            self.assertNotEqual(test_field_left,
                                test_field_right,
                                "BTSNumRepeaterField objects are equal but they shouldn't be!")

        test_field = tekton_compressor.BTSNumRepeaterField()
        with self.assertRaises(TypeError):
            test_field == "A string"

    def test_field_header_and_reps_bytes(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_bts_num_repeater_field',
                                     'test_field_header_and_reps_bytes'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_field = tekton_compressor.BTSNumRepeaterField()
            test_field.num_reps = test_case["num_reps"]
            expected_result = int_list_to_bytes(test_case["expected_result"])
            self.assertEqual(test_field.field_header_and_reps_bytes,
                             expected_result,
                             "BTSNumRepeaterField field_header_and_reps_bytes did not match expected result.")


    def test_bts_number_byte(self):
        test_field = tekton_compressor.BTSNumRepeaterField()
        test_field.bts_num = 0x7e
        expected_result = (0x7e).to_bytes(1, byteorder="big")
        self.assertEqual(expected_result, test_field.bts_number_byte,
                         "BTSNumRepeaterField BTS Number Byte did not match expected result.")

    def test_compressed_data(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_bts_num_repeater_field',
                                     'test_compressed_data'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field = tekton_compressor.BTSNumRepeaterField()
            test_field.num_reps = test_item["num_reps"]
            test_field.bts_num = test_item["bts_num"]

            test_result = test_field.compressed_data
            expected_result = int_list_to_bytes(test_item["expected_result"])
            self.assertEqual(expected_result,
                             test_result,
                             "Error when compressing BTSNumRepeaterField {}".format(test_item))

    def _get_fields_from_eq_test_data(self, test_item):
        test_field_left = tekton_compressor.BTSNumRepeaterField()
        test_field_right = tekton_compressor.BTSNumRepeaterField()

        test_field_left.bts_num = test_item["left"]["bts_num"]
        test_field_left.num_reps = test_item["left"]["num_reps"]

        test_field_right.bts_num = test_item["right"]["bts_num"]
        test_field_right.num_reps = test_item["right"]["num_reps"]

        return test_field_left, test_field_right


class TestBTSNumSingleField(unittest.TestCase):
    def test_init(self):
        test_field = tekton_compressor.BTSNumSingleField()
        self.assertTrue(isinstance(test_field, tekton_compressor.BTSNumSingleField))
        self.assertEqual(0x00, test_field.bts_num, "BTSNumSingleField bts_num did not initialize to 0x00!")

    def test_eq(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_bts_num_single_field',
                                     'test_eq'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field_left, test_field_right = self._get_fields_from_eq_test_data(test_item)
            self.assertEqual(test_field_left,
                             test_field_right,
                             "BTSNumSingleField objects should be equal but they're not!")

    def test_ne(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_bts_num_single_field',
                                     'test_ne'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field_left, test_field_right = self._get_fields_from_eq_test_data(test_item)
            self.assertNotEqual(test_field_left,
                                test_field_right,
                                "BTSNumSingleField objects should not be equal but they are!")

        test_field = tekton_compressor.BTSNumRepeaterField()
        with self.assertRaises(TypeError):
            test_field != "A string"

    def test_field_header_byte(self):
        test_field = tekton_compressor.BTSNumSingleField()
        expected_result = b'\x00'
        actual_result = test_field.field_header_byte
        self.assertEqual(expected_result,
                         actual_result,
                         "BTSNumSingleField did not generate correct field header byte!")

    def test_bts_number_byte(self):
        test_field = tekton_compressor.BTSNumSingleField()
        test_field.bts_num = 0xc5
        expected_result = (0xc5).to_bytes(1, byteorder="big")
        self.assertEqual(expected_result, test_field.bts_number_byte,
                         "BTSNumSingleField BTS Number Byte did not match expected result.")

    def test_compressed_data(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_compressor',
                                     'test_bts_num_single_field',
                                     'test_compressed_data'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field = tekton_compressor.BTSNumSingleField()
            test_field.bts_num = test_item["bts_num"]

            test_result = test_field.compressed_data
            expected_result = int_list_to_bytes(test_item["expected_result"])
            self.assertEqual(expected_result,
                             test_result,
                             "Error when compressing BTSNumSingleField {}".format(test_item))

    def _get_fields_from_eq_test_data(self, test_item):
        test_field_left = tekton_compressor.BTSNumRepeaterField()
        test_field_right = tekton_compressor.BTSNumRepeaterField()

        test_field_left.bts_num = test_item["left"]["bts_num"]
        test_field_right.bts_num = test_item["right"]["bts_num"]

        return test_field_left, test_field_right
