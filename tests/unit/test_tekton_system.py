from context import tekton
from tekton import tekton_system
import unittest


class TestTektonSystem(unittest.TestCase):
    def test_lorom_to_pc(self):
        test_lorom = 0xc3bcd2
        expected_result = 2211026
        actual_result = tekton_system.lorom_to_pc(test_lorom)

        self.assertEqual(expected_result, actual_result, "LoROM to PC returned incorrect value!")

        with self.assertRaises(TypeError):
            tekton_system.lorom_to_pc("c3bcd2")
        with self.assertRaises(ValueError):
            tekton_system.lorom_to_pc(-5)
        with self.assertRaises(ValueError):
            tekton_system.lorom_to_pc(0xffffffff)

    def test_overwrite_bytes_at_index(self):
        original_string = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        replace_string = b'\x11\x22\x33\x44'
        replace_start_index = 0x02

        expected_result = b'\x00\x00\x11\x22\x33\x44\x00\x00'
        actual_result = tekton_system.overwrite_bytes_at_index(original_string, replace_string, replace_start_index)

        self.assertEqual(expected_result, actual_result, "Byte string was not correctly replaced at index {}".format(replace_start_index))