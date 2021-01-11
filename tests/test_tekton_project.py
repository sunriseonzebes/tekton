from testing_common import tekton, original_rom_path, load_test_data_dir, int_list_to_bytes
from tekton import tekton_project, tekton_room_dict, tekton_room, tekton_door
import hashlib
import modified_test_roms
import os
import yaml
import unittest


class TestTektonProjectUnit(unittest.TestCase):
    def test_init(self):
        test_proj = tekton_project.TektonProject()
        self.assertNotEqual(test_proj, None, "Test Project is None!")
        self.assertEqual(test_proj.source_rom_path, None, "Source ROM is not an empty string!")
        self.assertTrue(isinstance(test_proj.rooms, tekton_room_dict.TektonRoomDict), "Rooms is not a TektonRoomDict!")

    def test_original_rom_exists(self):
        error_msg = "Original ROM not found in test fixtures folder! \n" \
                    "You may need to copy the original Super Metroid ROM to {}".format(original_rom_path)
        self.assertTrue(os.path.exists(original_rom_path), msg=error_msg)

    def test_get_source_rom_contents(self):
        original_rom_md5 = b'\x21\xf3\xe9\x8d\xf4\x78\x0e\xe1\xc6\x67\xb8\x4e\x57\xd8\x86\x75'
        test_project = tekton_project.TektonProject()
        test_project.source_rom_path = original_rom_path

        with open(original_rom_path, "rb") as f:
            expected_result = f.read()
        actual_result = test_project.get_source_rom_contents()

        # Test that the ROM from fixtures is being returned here
        self.assertEqual(expected_result, actual_result, "Original ROM did not import correctly!")

        # Test that the ROM md5 hash equals the hash of the community standard ROM
        self.assertEqual(original_rom_md5,
                         hashlib.md5(actual_result).digest(),
                         "Original ROM does not have correct hash!")


class TestTektonProjectIntegration(unittest.TestCase):
    def test_write_modified_rom(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'integration',
                                     'test_tekton_project',
                                     'test_write_modified_contents'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_proj = tekton_project.TektonProject()
            test_proj.source_rom_path = original_rom_path

            for test_room_data in test_item["rooms"]:
                new_room = tekton_room.TektonRoom(test_room_data["width"], test_room_data["height"])
                new_room.header = test_room_data["header"]
                new_room.level_data_address = test_room_data["level_data_address"]
                if "level_data_length" in test_room_data.keys():
                    new_room.level_data_length = test_room_data["level_data_length"]
                if "doors" in test_room_data.keys():
                    for test_door_data in test_room_data["doors"]:
                        new_door = tekton_door.TektonDoor()
                        new_door.data_address = test_door_data["data_address"]
                        new_door.target_room_id = test_door_data["target_room_id"]
                        new_door.bit_flag = test_door_data["bit_flag"]
                        new_door.exit_direction = test_door_data["exit_direction"]
                        new_door.target_door_cap_col = test_door_data["target_door_cap_col"]
                        new_door.target_door_cap_row = test_door_data["target_door_cap_row"]
                        new_door.target_room_screen_h = test_door_data["target_room_screen_h"]
                        new_door.target_room_screen_v = test_door_data["target_room_screen_v"]
                        new_door.distance_to_spawn = test_door_data["distance_to_spawn"]
                        new_door.asm_pointer = test_door_data["asm_pointer"]
                        new_room.doors.append(new_door)
                test_proj.rooms.add_room(new_room)

            deltas = []
            for delta in test_item["deltas"]:
                new_delta = modified_test_roms.ROMDelta(delta["address"],
                                                        int_list_to_bytes(delta["bytes"]))
                if "pad" in delta.keys():
                    new_delta.pad = delta["pad"]
                if "pad_byte" in delta.keys():
                    new_delta.pad = int_list_to_bytes(delta["pad_byte"])
                deltas.append(new_delta)

            # Collect results
            expected_result = modified_test_roms.get_modified_rom_contents(deltas)
            actual_result = test_proj.get_modified_rom_contents()

            output_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "fixtures", "modified_rom.sfc")
            with open(output_path, "wb") as out_file:
                out_file.write(actual_result)

            self.assertEqual(expected_result, actual_result, "Output ROM did not match expected result!")

    def test_import_rooms(self):
        # Default Rooms
        test_project = tekton_project.TektonProject()
        test_project.source_rom_path = original_rom_path
        test_project.import_rooms()
        test_data = self._get_room_import_test_data()

        for test_item in test_data:
            room_header = test_item["header"]
            self.assertTrue(isinstance(test_project.rooms[room_header], tekton_room.TektonRoom),
                            msg="Room {} was not created on import!".format(hex(room_header)))
            self._test_room_properties(test_project.rooms[room_header], test_item)

        # Custom Rooms
        test_project = tekton_project.TektonProject()
        test_project.source_rom_path = original_rom_path
        test_yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "fixtures",
                                      "integration",
                                      "room_imports",
                                      "custom_room_header_import.yaml")
        test_project.import_rooms(test_yaml_path)
        test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "fixtures",
                                     "integration",
                                     "room_imports",
                                     "test_custom_headers")
        test_data = self._get_room_import_test_data(test_data_dir)

        for test_item in test_data:
            room_header = test_item["header"]
            self.assertTrue(isinstance(test_project.rooms[room_header], tekton_room.TektonRoom),
                            msg="Room {} was not created on import!".format(hex(room_header)))
            self._test_room_properties(test_project.rooms[room_header], test_item)

    def _get_room_import_test_data(self, test_data_dir=None):
        if test_data_dir is None:
            test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "fixtures",
                                         "integration",
                                         "room_imports",
                                         "original_rom"
                                         )
        test_data = []
        for filename in os.listdir(test_data_dir):
            with open(os.path.join(test_data_dir, filename)) as f:
                test_data.append(yaml.full_load(f))

        return test_data

    def _test_room_properties(self, test_room, expected_values):
        self.assertEqual(expected_values["header"],
                         test_room.header,
                         "Room {} did not import correct header.".format(hex(expected_values["header"])))
        if "name" in expected_values.keys():
            self.assertEqual(expected_values["name"],
                             test_room.name,
                             "Room {} did not import correct name.".format(hex(expected_values["header"])))
        self.assertEqual(expected_values["width"],
                         test_room.width_screens,
                         "Room {} did not import correct width.".format(hex(expected_values["header"])))
        self.assertEqual(expected_values["height"],
                         test_room.height_screens,
                         "Room {} did not import correct height.".format(hex(expected_values["header"])))
        self.assertEqual(expected_values["level_data_address"],
                         test_room.level_data_address,
                         "Room {} did not import correct level data address.".format(hex(expected_values["header"])))
