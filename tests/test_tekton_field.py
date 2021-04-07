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


class TestTektonWordFillField(unittest.TestCase):
    def test_init(self):
        test_field = tekton_field.TektonWordFillField()
        self.assertTrue(isinstance(test_field, tekton_field.TektonWordFillField))
        self.assertEqual(b'\x00\x00', test_field._word, "TektonWordFillField _word did not initialize correctly!")

    def test_word(self):
        test_field = tekton_field.TektonWordFillField()
        test_field.word = b'\xaf\x46'
        self.assertEqual(b'\xaf\x46', test_field.word, "TektonWordFillField word returned wrong value!")
        test_field.word = 0xaf46
        self.assertEqual(b'\xaf\x46', test_field.word, "TektonWordFillField word returned wrong value!")
        with self.assertRaises(TypeError):
            test_field.word = "A string."
        with self.assertRaises(ValueError):
            test_field.word = b'\x12'
        with self.assertRaises(ValueError):
            test_field.word = b'\x12\x34\x56'
        with self.assertRaises(ValueError):
            test_field.word = -1
        with self.assertRaises(ValueError):
            test_field.word = 70000

    def test_compressed_data(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_field',
                                     'test_tekton_word_fill_field',
                                     'test_compressed_data'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            test_field = tekton_field.TektonWordFillField()
            test_field.num_bytes = test_case["num_bytes"]
            test_field.word = int_list_to_bytes(test_case["word"])
            expected_result = int_list_to_bytes(test_case["expected_result"])
            actual_result = test_field.compressed_data
            self.assertEqual(expected_result, actual_result, "TektonWordFillField did not compress correctly!")
