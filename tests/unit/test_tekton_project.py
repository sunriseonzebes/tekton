from context import tekton
from tekton import tekton_project, tekton_room_dict
import hashlib
import os
import unittest

class TestTektonProject(unittest.TestCase):
    def setUp(self):
        self.original_rom_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures', 'original_rom.sfc')

    def test_init(self):
        test_proj = tekton_project.TektonProject()
        self.assertNotEqual(test_proj, None, "Test Project is None!")
        self.assertEqual(test_proj.source_rom_path, None, "Source ROM is not an empty string!")
        self.assertTrue(isinstance(test_proj.rooms, tekton_room_dict.TektonRoomDict), "Rooms is not a TektonRoomDict!")

    def test_original_rom_exists(self):
        error_msg = "Original ROM not found in test fixtures folder! \n" \
                    "You may need to copy the original Super Metroid ROM to {}".format(self.original_rom_path)
        self.assertTrue(os.path.exists(self.original_rom_path), msg=error_msg)

    def test_get_source_rom_contents(self):
        original_rom_md5 = b'\x21\xf3\xe9\x8d\xf4\x78\x0e\xe1\xc6\x67\xb8\x4e\x57\xd8\x86\x75'
        test_project = tekton_project.TektonProject()
        test_project.source_rom_path = self.original_rom_path

        with open(self.original_rom_path, "rb") as f:
            expected_result = f.read()
        actual_result = test_project.get_source_rom_contents()

        # Test that the ROM from fixtures is being returned here
        self.assertEqual(expected_result, actual_result, "Original ROM did not import correctly!")

        # Test that the ROM md5 hash equals the hash of the community standard ROM
        self.assertEqual(original_rom_md5,
                         hashlib.md5(actual_result).digest(),
                         "Original ROM does not have correct hash!")

