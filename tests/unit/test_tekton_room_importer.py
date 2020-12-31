from context import tekton, original_rom_path
from tekton import tekton_room_importer, tekton_room, tekton_system, tekton_door
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
                "level_data_address": 0x231f4b
            },
            {
                "header": 0x792fd,  # Parlor and Alcatraz
                "width": 5,
                "height": 5,
                "level_data_address": 0x215bc4
            }
        ]

        for test_item in test_data:
            print(hex(test_item["header"]))
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

    def test_get_door_data_addresses(self):
        with open(original_rom_path, "rb") as f:
            rom_contents = f.read()

        test_data = [
            {
                "room_header_address": 0x795d4,  # Crateria Tube
                "door_addresses": [0x18ac6, 0x18ad2],
                "num_doors": 2
            }
        ]

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

        test_data = [
            {
                "door_address": 0x18ac6,  # Door 00 in Crateria Tube (795d4)
                "expected_results": {
                    "room_id": 0x791f8,
                    "bit_flag": tekton_system.DoorBitFlag.DOOR_SAME_AREA,
                    "direction": tekton_system.DoorExitDirection.LEFT,
                    "door_cap_x": 0x8e,
                    "door_cap_y": 0x46,
                    "screen_x": 0x08,
                    "screen_y": 0x04,
                    "distance_to_spawn": 0x8000,
                    "asm_pointer": 0x0000
                }
            },
            {
                "door_address": 0x189be,  # Door 00 in Crateria Save Room (793d5)
                "expected_results": {
                    "room_id": 0x792fd,
                    "bit_flag": tekton_system.DoorBitFlag.DOOR_SAME_AREA,
                    "direction": tekton_system.DoorExitDirection.RIGHT,
                    "door_cap_x": 0x11,
                    "door_cap_y": 0x26,
                    "screen_x": 0x01,
                    "screen_y": 0x02,
                    "distance_to_spawn": 0x8000,
                    "asm_pointer": 0xb981
                }
            },
            {
                "door_address": 0x1911a,  # Door 01 in Below Spazer (7a408)
                "expected_results": {
                    "room_id": 0x7cf54,
                    "bit_flag": tekton_system.DoorBitFlag.DOOR_AREA_CHANGE,
                    "direction": tekton_system.DoorExitDirection.RIGHT,
                    "door_cap_x": 0x01,
                    "door_cap_y": 0x06,
                    "screen_x": 0x00,
                    "screen_y": 0x00,
                    "distance_to_spawn": 0x8000,
                    "asm_pointer": 0x0000
                }
            }
        ]

        for test_item in test_data:
            test_door = tekton_room_importer.import_door(rom_contents, test_item["door_address"])
            self.assertTrue(isinstance(test_door, tekton_door.TektonDoor), msg="TektonDoor object not instantiated!")
            self.assertEqual(test_item["door_address"], test_door.data_address, "Door has incorrect data address!")
            expected_results = test_item["expected_results"]
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