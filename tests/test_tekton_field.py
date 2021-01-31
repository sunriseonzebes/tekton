from testing_common import tekton, load_test_data_dir, int_list_to_bytes
from tekton import tekton_field
import os
import unittest

class TestTektonField(unittest.TestCase):
    def test_init(self):
        test_field = tekton_field.TektonField()
        self.assertEqual(1, test_field._num_bytes, "TektonField _num_bytes did not initialize properly!")
        self.assertEqual(0b000, tekton_field.TektonField.command_code, "TektonField.command_code is not correct!")
        self.assertEqual(0b111,
                         tekton_field.TektonField.extended_command_code,
                         "TektonField.extended_command_code is not correct!")

    def test_num_bytes(self):
        test_field = tekton_field.TektonField()
        test_field.num_bytes = 15
        self.assertEqual(15, test_field.num_bytes)

        with self.assertRaises(ValueError, msg="TektonField num_bytes should not allow numbers less than 1."):
            test_field.num_bytes = 0
        with self.assertRaises(ValueError, msg="TektonField num_bytes should not allow numbers greater than 1023."):
            test_field.num_bytes = 2048
        with self.assertRaises(TypeError, msg="TektonField num_bytes should only allow int."):
            test_field.num_bytes = "A string."
        with self.assertRaises(TypeError, msg="TektonField num_bytes should only allow int."):
            test_field.num_bytes = 2.63

    def test_cmd_and_reps_bytes(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_field',
                                     'test_tekton_field',
                                     'test_cmd_and_reps_bytes'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_field = tekton_field.TektonField()
            test_field.command_code = test_case["command_code"]
            test_field.num_bytes = test_case["num_bytes"]
            expected_result = int_list_to_bytes(test_case["expected_result"])
            actual_result = test_field.cmd_and_reps_bytes
            self.assertEqual(expected_result, actual_result, "cmd_and_reps_bytes did not return correct result!")


class TestTektonDirectCopyField(unittest.TestCase):
    def test_init(self):
        test_field = tekton_field.TektonDirectCopyField()
        self.assertTrue(isinstance(test_field, tekton_field.TektonDirectCopyField))
        self.assertEqual(b'\x00',
                         test_field._bytes_data,
                         "TektonDirectCopyField _bytes_string did not initialize correctly!")

    def test_bytes_data(self):
        test_field = tekton_field.TektonDirectCopyField()
        test_field.bytes_data = b'\x0a\x2f'
        self.assertEqual(b'\x0a\x2f',
                         test_field.bytes_data,
                         "TektonDirectCopyField bytes_string was not set properly!")
        test_field.bytes_data = 0x0a2f
        self.assertEqual(b'\x0a\x2f',
                         test_field.bytes_data,
                         "TektonDirectCopyField bytes_string was not set properly!")
        with self.assertRaises(TypeError):
            test_field.bytes_data = "A string."
        with self.assertRaises(ValueError):
            test_field.bytes_data = b''
        with self.assertRaises(ValueError):
            test_field.bytes_data = -1

    def test_compressed_data(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_field',
                                     'test_tekton_direct_copy_field',
                                     'test_compressed_data'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_field = tekton_field.TektonDirectCopyField()
            test_field.bytes_data = int_list_to_bytes(test_case["bytes_data"])
            expected_result = int_list_to_bytes(test_case["expected_result"])
            actual_result = test_field.compressed_data
            self.assertEqual(expected_result, actual_result, "TektonDirectCopyField compressed_data is wrong!")



class TestTektonByteFillField(unittest.TestCase):
    def test_init(self):
        test_field = tekton_field.TektonByteFillField()
        self.assertTrue(isinstance(test_field, tekton_field.TektonByteFillField))
        self.assertEqual(1, test_field.num_bytes, "TektonByteFilLField num_bytes initialized with incorrect value!")
        self.assertEqual(b'\x00', test_field._byte, "TektonByteFilLField byte initialized with incorrect value!")

    def test_byte(self):
        test_field = tekton_field.TektonByteFillField()
        test_field.byte = b'\xaf'
        self.assertEqual(b'\xaf', test_field.byte, "TektonByteFillField byte was not set properly!")
        test_field.byte = 0x4d
        self.assertEqual(b'\x4d', test_field.byte, "TektonByteFillField byte was not set properly!")
        with self.assertRaises(TypeError):
            test_field.byte = "A string."
        with self.assertRaises(ValueError):
            test_field.byte = b''
        with self.assertRaises(ValueError):
            test_field.byte = b'\x12\x34'
        with self.assertRaises(ValueError):
            test_field.byte = -1
        with self.assertRaises(ValueError):
            test_field.byte = 0x1234

    def test_compressed_data(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_field',
                                     'test_tekton_byte_fill_field',
                                     'test_compressed_data'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_field = tekton_field.TektonByteFillField()
            test_field.num_bytes = test_case["num_bytes"]
            test_field.byte = test_case["byte"]
            expected_result = int_list_to_bytes(test_case["expected_result"])
            actual_result = test_field.compressed_data
            self.assertEqual(expected_result, actual_result, "TektonByteFillField did not compress correctly!")



class TestTektonL1RepeaterField(unittest.TestCase):
    def test_init(self):
        test_field = tekton_field.TektonL1RepeaterField()
        self.assertTrue(isinstance(test_field, tekton_field.TektonL1RepeaterField))
        self.assertEqual(0, test_field.num_reps, "L1RepeaterField num_reps did not initialize to 0!")
        self.assertEqual(0x00, test_field.bts_type, "L1RepeaterField bts_type did not initialize to 0!")
        self.assertFalse(test_field.h_mirror, msg="L1RepeaterField h_mirror did not initialize to False!")
        self.assertFalse(test_field.v_mirror, msg="L1RepeaterField v_mirror did not initialize to False!")
        self.assertEqual(0x00, test_field._tileno, "L1RepeaterField _tileno did not initialize to 0!")

    def test_eq(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_field',
                                     'test_l1_repeater_field',
                                     'test_eq'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field_left, test_field_right = self._get_fields_from_eq_test_data(test_item)
            self.assertEqual(test_field_left,
                             test_field_right,
                             "L1RepeaterField objects should be equal but they're not!")

        test_field = tekton_field.TektonL1RepeaterField()
        with self.assertRaises(TypeError):
            test_field == "A string"

    def test_ne(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_field',
                                     'test_l1_repeater_field',
                                     'test_ne'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field_left, test_field_right = self._get_fields_from_eq_test_data(test_item)
            self.assertNotEqual(test_field_left,
                                test_field_right,
                                "L1RepeaterField objects are equal but they shouldn't be!")

        test_field = tekton_field.TektonL1RepeaterField()
        with self.assertRaises(TypeError):
            test_field != "A string"

    def test_tileno(self):
        test_field = tekton_field.TektonL1RepeaterField()
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
                                     'test_tekton_field',
                                     'test_l1_repeater_field',
                                     'test_field_header_and_reps_bytes'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field = tekton_field.TektonL1RepeaterField()
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
                                     'test_tekton_field',
                                     'test_l1_repeater_field',
                                     'test_attributes_bytes'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_field = tekton_field.TektonL1RepeaterField()
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
                                     'test_tekton_field',
                                     'test_l1_repeater_field',
                                     'test_compressed_data'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field = tekton_field.TektonL1RepeaterField()
            test_field.tileno = test_item["tileno"]
            test_field.bts_type = test_item["bts"]
            test_field.h_mirror = test_item['h_mirror']
            test_field.v_mirror = test_item['v_mirror']
            test_field.num_reps = test_item["num_reps"]

            test_result = test_field.compressed_data
            expected_result = int_list_to_bytes(test_item["expected_result"])
            self.assertEqual(expected_result, test_result, "Error when compressing L1RepeaterField{}".format(test_item))

    def _get_fields_from_eq_test_data(self, test_item):
        test_field_left = tekton_field.TektonL1RepeaterField()
        test_field_right = tekton_field.TektonL1RepeaterField()

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


class TestTektonBTSNumRepeaterField(unittest.TestCase):
    def test_init(self):
        test_field = tekton_field.TektonBTSNumRepeaterField()
        self.assertTrue(isinstance(test_field, tekton_field.TektonBTSNumRepeaterField))
        self.assertEqual(0, test_field.num_reps, "BTSNumRepeaterField num_reps did not initialize to 0!")
        self.assertEqual(0x00, test_field.bts_num, "BTSNumRepeaterField bts_type did not initialize to 0!")

    def test_eq(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_field',
                                     'test_bts_num_repeater_field',
                                     'test_eq'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field_left, test_field_right = self._get_fields_from_eq_test_data(test_item)
            self.assertEqual(test_field_left,
                             test_field_right,
                             "BTSNumRepeaterField objects should be equal but they're not!")

        test_field = tekton_field.TektonBTSNumRepeaterField()
        with self.assertRaises(TypeError):
            test_field == "A string"

    def test_ne(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_field',
                                     'test_bts_num_repeater_field',
                                     'test_ne'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field_left, test_field_right = self._get_fields_from_eq_test_data(test_item)
            self.assertNotEqual(test_field_left,
                                test_field_right,
                                "BTSNumRepeaterField objects are equal but they shouldn't be!")

        test_field = tekton_field.TektonBTSNumRepeaterField()
        with self.assertRaises(TypeError):
            test_field == "A string"

    def test_field_header_and_reps_bytes(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_field',
                                     'test_bts_num_repeater_field',
                                     'test_field_header_and_reps_bytes'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_field = tekton_field.TektonBTSNumRepeaterField()
            test_field.num_reps = test_case["num_reps"]
            expected_result = int_list_to_bytes(test_case["expected_result"])
            self.assertEqual(test_field.field_header_and_reps_bytes,
                             expected_result,
                             "BTSNumRepeaterField field_header_and_reps_bytes did not match expected result.")


    def test_bts_number_byte(self):
        test_field = tekton_field.TektonBTSNumRepeaterField()
        test_field.bts_num = 0x7e
        expected_result = (0x7e).to_bytes(1, byteorder="big")
        self.assertEqual(expected_result, test_field.bts_number_byte,
                         "BTSNumRepeaterField BTS Number Byte did not match expected result.")

    def test_compressed_data(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_field',
                                     'test_bts_num_repeater_field',
                                     'test_compressed_data'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field = tekton_field.TektonBTSNumRepeaterField()
            test_field.num_reps = test_item["num_reps"]
            test_field.bts_num = test_item["bts_num"]

            test_result = test_field.compressed_data
            expected_result = int_list_to_bytes(test_item["expected_result"])
            self.assertEqual(expected_result,
                             test_result,
                             "Error when compressing BTSNumRepeaterField {}".format(test_item))

    def _get_fields_from_eq_test_data(self, test_item):
        test_field_left = tekton_field.TektonBTSNumRepeaterField()
        test_field_right = tekton_field.TektonBTSNumRepeaterField()

        test_field_left.bts_num = test_item["left"]["bts_num"]
        test_field_left.num_reps = test_item["left"]["num_reps"]

        test_field_right.bts_num = test_item["right"]["bts_num"]
        test_field_right.num_reps = test_item["right"]["num_reps"]

        return test_field_left, test_field_right


class TestTektonBTSNumSingleField(unittest.TestCase):
    def test_init(self):
        test_field = tekton_field.TektonBTSNumSingleField()
        self.assertTrue(isinstance(test_field, tekton_field.TektonBTSNumSingleField))
        self.assertEqual(0x00, test_field.bts_num, "BTSNumSingleField bts_num did not initialize to 0x00!")

    def test_eq(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_field',
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
                                     'test_tekton_field',
                                     'test_bts_num_single_field',
                                     'test_ne'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field_left, test_field_right = self._get_fields_from_eq_test_data(test_item)
            self.assertNotEqual(test_field_left,
                                test_field_right,
                                "BTSNumSingleField objects should not be equal but they are!")

        test_field = tekton_field.TektonBTSNumRepeaterField()
        with self.assertRaises(TypeError):
            test_field != "A string"

    def test_field_header_byte(self):
        test_field = tekton_field.TektonBTSNumSingleField()
        expected_result = b'\x00'
        actual_result = test_field.field_header_byte
        self.assertEqual(expected_result,
                         actual_result,
                         "BTSNumSingleField did not generate correct field header byte!")

    def test_bts_number_byte(self):
        test_field = tekton_field.TektonBTSNumSingleField()
        test_field.bts_num = 0xc5
        expected_result = (0xc5).to_bytes(1, byteorder="big")
        self.assertEqual(expected_result, test_field.bts_number_byte,
                         "BTSNumSingleField BTS Number Byte did not match expected result.")

    def test_compressed_data(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_field',
                                     'test_bts_num_single_field',
                                     'test_compressed_data'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_field = tekton_field.TektonBTSNumSingleField()
            test_field.bts_num = test_item["bts_num"]

            test_result = test_field.compressed_data
            expected_result = int_list_to_bytes(test_item["expected_result"])
            self.assertEqual(expected_result,
                             test_result,
                             "Error when compressing BTSNumSingleField {}".format(test_item))

    def _get_fields_from_eq_test_data(self, test_item):
        test_field_left = tekton_field.TektonBTSNumRepeaterField()
        test_field_right = tekton_field.TektonBTSNumRepeaterField()

        test_field_left.bts_num = test_item["left"]["bts_num"]
        test_field_right.bts_num = test_item["right"]["bts_num"]

        return test_field_left, test_field_right