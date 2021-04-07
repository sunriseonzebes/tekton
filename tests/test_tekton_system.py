from testing_common import tekton, load_test_data_dir, int_list_to_bytes
from tekton import tekton_system
import os
import unittest


class TestTektonSystem(unittest.TestCase):
    def test_lorom_to_pc(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_system',
                                     'test_lorom_to_pc'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_lorom_value = int_list_to_bytes(test_item["lorom_value"])
            actual_result = tekton_system.lorom_to_pc(test_lorom_value, byteorder=test_item["byteorder"])
            self.assertEqual(test_item["expected_result"], actual_result, "LoROM to PC returned incorrect value!")

        with self.assertRaises(TypeError):
            tekton_system.lorom_to_pc("c3bcd2", byteorder="big")
        with self.assertRaises(TypeError):
            tekton_system.lorom_to_pc(0x8202ff, byteorder="big")
        with self.assertRaises(ValueError):
            tekton_system.lorom_to_pc(b'\xff\xff\xff\xff', byteorder="big")

    def test_pc_to_lorom(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_system',
                                     'test_pc_to_lorom'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            expected_result = int_list_to_bytes(test_case["expected_result"])
            actual_result = tekton_system.pc_to_lorom(test_case["pc_address"], byteorder=test_case["byteorder"])
            self.assertEqual(expected_result, actual_result, "pc_to_lorom returned incorrect result!")

    def test_overwrite_bytes_at_index(self):
        original_string = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        replace_string = b'\x11\x22\x33\x44'
        replace_start_index = 0x02

        expected_result = b'\x00\x00\x11\x22\x33\x44\x00\x00'
        actual_result = tekton_system.overwrite_bytes_at_index(original_string, replace_string, replace_start_index)

        self.assertEqual(expected_result, actual_result, "Byte string was not correctly replaced at index {}".format(replace_start_index))

    def test_pad_bytes(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_system',
                                     'test_pad_bytes'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            input_string = int_list_to_bytes(test_case["input_string"])
            min_length = test_case["min_length"]
            pad_byte = test_case["pad_byte"].to_bytes(1, byteorder="big")
            expected_result = int_list_to_bytes(test_case["expected_result"])
            actual_result = tekton_system.pad_bytes(input_string, min_length, pad_byte)
            self.assertEqual(expected_result, actual_result, "pad_bytes did not return the correct results!")