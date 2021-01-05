from testing_common import tekton, original_rom_path, load_test_data_dir
from tekton import tekton_room_importer, tekton_room, tekton_system, tekton_door
import os
import unittest


class TestTektonRoomImporter(unittest.TestCase):
    def test_import_room_from_rom(self):
        with open(original_rom_path, "rb") as f:
            rom_contents = f.read()
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_room_importer',
                                     'test_import_room_from_rom'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_room = tekton_room_importer.import_room_from_rom(rom_contents, test_item["header"])
            self.assertTrue(isinstance(test_room, tekton_room.TektonRoom))
            self.assertEqual(test_item["header"],
                             test_room.header,
                             "Room {} imported incorrect header address!".format(hex(test_item["header"])))
            self.assertEqual(test_item["width"],
                             test_room.width_screens,
                             "Room {} imported incorrect width value!".format(hex(test_item["header"])))
            self.assertEqual(test_item["height"],
                             test_room.height_screens,
                             "Room {} imported incorrect height value!".format(hex(test_item["header"])))
            self.assertEqual(test_item["level_data_address"],
                             test_room.level_data_address,
                             "Room {} imported incorrect level data address!".format(hex(test_item["header"])))

        with self.assertRaises(ValueError):
            test_room = tekton_room_importer.import_room_from_rom(rom_contents, 0x795d3)
        with self.assertRaises(TypeError):
            test_room = tekton_room_importer.import_room_from_rom(rom_contents, "795d4")

    def test_get_pointer_addresses(self):
        with open(original_rom_path, "rb") as f:
            rom_contents = f.read()
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_room_importer',
                                     'test_get_pointer_addresses'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for expected_result in test_data:
            actual_result = tekton_room_importer._get_data_addresses(rom_contents, expected_result["header"])
            self.assertEqual(expected_result,
                             actual_result,
                             "Room {} did not return the correct pointers!".format(hex(expected_result["header"])))

    def test_get_door_data_addresses(self):
        with open(original_rom_path, "rb") as f:
            rom_contents = f.read()
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_room_importer',
                                     'test_get_door_data_addresses'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            actual_result = tekton_room_importer._get_door_data_addresses(rom_contents,
                                                                         test_item["room_header_address"])

            actual_result = actual_result[0:test_item["num_doors"]]
            self.assertEqual(test_item["door_addresses"],
                             actual_result,
                             "Incorrect door list returned for room {}".format(test_item["room_header_address"]))

    def test_import_door(self):
        with open(original_rom_path, "rb") as f:
            rom_contents = f.read()
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_room_importer',
                                     'test_import_door'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_door = tekton_room_importer.import_door(rom_contents, test_item["door_address"])
            self.assertTrue(isinstance(test_door, tekton_door.TektonDoor), msg="TektonDoor object not instantiated!")
            self.assertEqual(test_item["door_address"], test_door.data_address, "Door has incorrect data address!")
            expected_results = test_item["expected_results"]
            expected_results["bit_flag"] = tekton_system.DoorBitFlag[expected_results["bit_flag"]]
            expected_results["direction"] = tekton_system.DoorExitDirection[expected_results["direction"]]
            self.assertEqual(expected_results["room_id"], test_door.target_room_id, "Door has wrong target room id!")
            self.assertEqual(expected_results["bit_flag"], test_door.bit_flag, "Door has wrong bit flag!")
            self.assertEqual(expected_results["direction"], test_door.exit_direction, "Door has wrong exit direction!")
            self.assertEqual(expected_results["door_cap_x"],
                             test_door.target_door_cap_col,
                             "Door has wrong exit door cap x coordinate!")
            self.assertEqual(expected_results["door_cap_y"],
                             test_door.target_door_cap_row,
                             "Door has wrong exit door cap y coordinate!")
            self.assertEqual(expected_results["screen_x"],
                             test_door.target_room_screen_h,
                             "Door has wrong target room horizontal screen!")
            self.assertEqual(expected_results["screen_y"],
                             test_door.target_room_screen_v,
                             "Door has wrong target room vertical screen!")
            self.assertEqual(expected_results["distance_to_spawn"],
                             test_door.distance_to_spawn,
                             "Door has wrong distance to spawn!")
            self.assertEqual(expected_results["asm_pointer"], test_door.asm_pointer, "Door has wrong ASM pointer!")

            with self.assertRaises(TypeError):
                test_door = tekton_room_importer.import_door(rom_contents, "0x18ac6")
            with self.assertRaises(ValueError):
                test_door = tekton_room_importer.import_door(rom_contents, -5)