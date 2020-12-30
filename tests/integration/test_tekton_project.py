from context import tekton, original_rom_path
from tekton import tekton_project, tekton_system, tekton_room_dict, tekton_room
import hashlib
import json
import modified_test_roms
import os
import unittest


class TestTektonProject(unittest.TestCase):
    def test_write_modified_rom(self):
        # Init Test Project
        test_proj = tekton_project.TektonProject()
        test_proj.source_rom_path = original_rom_path

        # Create a new Room 79D5A and add it to the project
        test_new_79d5a = tekton_room.TektonRoom(1, 1)
        test_new_79d5a.level_data_address = 0x21bcd2
        test_new_79d5a.level_data_length = 155
        test_proj.rooms.add_room(test_new_79d5a)

        # Collect results
        expected_result = modified_test_roms.get_modified_rom_contents("blank_room_79d5a")
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
            room_header = int(test_item["header"], 16)
            self.assertTrue(isinstance(test_project.rooms[room_header], tekton_room.TektonRoom),
                            msg="Room {} was not created on import!".format(hex(room_header)))
            self._test_room_properties(test_project.rooms[room_header], test_item)

        # Custom Rooms
        test_project = tekton_project.TektonProject()
        test_project.source_rom_path = original_rom_path
        test_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "fixtures",
                                      "room_imports",
                                      "custom_room_header_import.json")
        test_project.import_rooms(test_json_path)
        test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "fixtures",
                                      "room_imports",
                                      "test_custom_headers")
        test_data = self._get_room_import_test_data(test_data_dir)

        for test_item in test_data:
            room_header = int(test_item["header"], 16)
            self.assertTrue(isinstance(test_project.rooms[room_header], tekton_room.TektonRoom),
                            msg="Room {} was not created on import!".format(hex(room_header)))
            self._test_room_properties(test_project.rooms[room_header], test_item)

    def _get_room_import_test_data(self, test_data_dir=None):
        if test_data_dir is None:
            test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "fixtures",
                                         "room_imports",
                                         "original_rom"
                                         )
        test_data = []
        for filename in os.listdir(test_data_dir):
            with open(os.path.join(test_data_dir, filename)) as f:
                test_data.append(json.load(f))

        return test_data

    def _test_room_properties(self, test_room, expected_values):
        self.assertEqual(int(expected_values["header"], 16),
                         test_room.header,
                         "Room {} did not import correct header.".format(expected_values["header"]))
        if "name" in expected_values.keys():
            self.assertEqual(expected_values["name"],
                             test_room.name,
                             "Room {} did not import correct name.".format(expected_values["header"]))
        self.assertEqual(expected_values["width"],
                         test_room.width_screens,
                         "Room {} did not import correct width.".format(expected_values["header"]))
        self.assertEqual(expected_values["height"],
                         test_room.height_screens,
                         "Room {} did not import correct height.".format(expected_values["header"]))
        self.assertEqual(int(expected_values["level_data_address"], 16),
                         test_room.level_data_address,
                         "Room {} did not import correct level data address.".format(expected_values["header"]))
