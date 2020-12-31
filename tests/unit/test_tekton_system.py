from context import tekton
from tekton import tekton_system
import unittest


class TestTektonSystem(unittest.TestCase):
    def test_lorom_to_pc(self):

        test_data = [
            {
                "expected_result": 0x21bcd2,
                "lorom_value": b'\xc3\xbc\xd2',
                "byteorder": "big"
            },
            {
                "expected_result": 0x21bcd2,
                "lorom_value": b'\xd2\xbc\xc3',
                "byteorder": "little"
            },
            {
                "expected_result": 0x231f4b,
                "lorom_value": b'\xc6\x9f\x4b',
                "byteorder": "big"
            },
            {
                "expected_result": 0x231f4b,
                "lorom_value": b'\xc6\x1f\x4b',
                "byteorder": "big"
            }
        ]

        for test_item in test_data:
            actual_result = tekton_system.lorom_to_pc(test_item["lorom_value"], byteorder=test_item["byteorder"])
            self.assertEqual(test_item["expected_result"], actual_result, "LoROM to PC returned incorrect value!")

        with self.assertRaises(TypeError):
            tekton_system.lorom_to_pc("c3bcd2", byteorder="big")
        with self.assertRaises(TypeError):
            tekton_system.lorom_to_pc(0x8202ff, byteorder="big")
        with self.assertRaises(ValueError):
            tekton_system.lorom_to_pc(b'\xff\xff\xff\xff', byteorder="big")


    def test_overwrite_bytes_at_index(self):
        original_string = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        replace_string = b'\x11\x22\x33\x44'
        replace_start_index = 0x02

        expected_result = b'\x00\x00\x11\x22\x33\x44\x00\x00'
        actual_result = tekton_system.overwrite_bytes_at_index(original_string, replace_string, replace_start_index)

        self.assertEqual(expected_result, actual_result, "Byte string was not correctly replaced at index {}".format(replace_start_index))