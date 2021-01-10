from testing_common import tekton, original_rom_path, load_test_data_dir, int_list_to_bytes
from tekton import tekton_room_importer, tekton_room, tekton_system, tekton_door
from pydoc import locate
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
            # TODO: Make this assertEqual once I figure out how to tell where door data ends
            self.assertLessEqual(len(test_item["doors"]),
                             len(test_room.doors),
                             "Test room {0} expected to import {1} doors, but imported {2}!\n{3}".format(
                    hex(test_item["header"]),
                    len(test_item["doors"]),
                    len(test_room.doors),
                    [hex(door.data_address) for door in test_room.doors]
                ))
            for i in range(len(test_item["doors"])):
                expected_door_address = test_item['doors'][i]
                actual_door = test_room.doors[i]
                self.assertEqual(expected_door_address,
                                 actual_door.data_address,
                                 "Door {} imported incorrect data address!".format(i))




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

    def test_import_door(self): # TODO: Split this into three tests: import door, _import_simple_door, _import_elevator_launchpad
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
            expected_results = test_item["expected_results"]
            self.assertTrue(isinstance(test_door, locate(expected_results["type"])),
                            msg="Door at address {0} is type {1}, expected {2}".format(
                                hex(test_item["door_address"]),
                                type(test_door),
                                expected_results["type"]
                            ))
            self.assertEqual(test_item["door_address"], test_door.data_address, "Door has incorrect data address!")
            if isinstance(test_door, tekton_door.TektonDoor):
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
            if isinstance(test_door, tekton_door.TektonElevatorLaunchpad):
                self.assertEqual(int_list_to_bytes(expected_results["door_data"]),
                                 test_door.door_data,
                                 "Elevator Launchpad has incorrect door data!")

            with self.assertRaises(TypeError):
                test_door = tekton_room_importer.import_door(rom_contents, "0x18ac6")
            with self.assertRaises(ValueError):
                test_door = tekton_room_importer.import_door(rom_contents, -5)