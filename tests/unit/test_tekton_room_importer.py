from context import tekton, original_rom_path
from tekton import tekton_room_importer, tekton_room
import unittest


class TestTektonRoomImporter(unittest.TestCase):
    def test_import_room_from_rom(self):
        with open(original_rom_path, "rb") as f:
            rom_contents = f.read()

        test_data = [
            {
                "header": 0x795d4,  # Crateria Tube
                "width": 1,
                "height": 1,
                "level_data_address": 0x21bcd2
            },
            {
                "header": 0x799bd,  # Green Pirates Shaft
                "width": 1,
                "height": 7,
                "level_data_address": 0x21ee60
            },
            {
                "header": 0x7a322,  # Red Tower Elevator Room
                "width": 3,
                "height": 8,
                "level_data_address": 0x239f4b
            },
            {
                "header": 0x792fd,  # Parlor and Alcatraz
                "width": 5,
                "height": 5,
                "level_data_address": 0x21dbc4
            }
        ]

        for test_item in test_data:
            test_room = tekton_room_importer.import_room_from_rom(rom_contents, test_item["header"])
            self.assertTrue(isinstance(test_room, tekton_room.TektonRoom))
            self.assertEqual(test_item["header"], test_room.header, "Test room imported incorrect header address!")
            self.assertEqual(test_item["width"], test_room.width_screens, "Test room imported incorrect width value!")
            self.assertEqual(test_item["height"], test_room.height_screens, "Test room imported incorrect height value!")
            self.assertEqual(test_item["level_data_address"],
                             test_room.level_data_address,
                             "Test room imported incorrect level data address!")

        with self.assertRaises(ValueError):
            test_room = tekton_room_importer.import_room_from_rom(rom_contents, 0x795d3)
        with self.assertRaises(TypeError):
            test_room = tekton_room_importer.import_room_from_rom(rom_contents, "795d4")

    def test_get_pointer_addresses(self):
        with open(original_rom_path, "rb") as f:
            rom_contents = f.read()

        test_data = [
            {
                "doors": 0x795fb,
                "events_pointers": [],
                "events_room_states": [],
                "header": 0x795d4,  # Crateria Tube
                "standard": 0x795df
            },
            {
                "doors": 0x79362,
                "events_pointers": [0x79308, 0x7930d],
                "events_room_states": [0x7932e, 0x79348],
                "header": 0x792fd,  # Parlor and Alcatraz
                "standard": 0x79312
            }
        ]

        for expected_result in test_data:
            actual_result = tekton_room_importer._get_data_addresses(rom_contents, expected_result["header"])
            self.assertEqual(expected_result,
                             actual_result,
                             "Room {} did not return the correct pointers!".format(hex(expected_result["header"])))

    def test_import_doors(self):
        with open(original_rom_path, "rb") as f:
            rom_contents = f.read()

