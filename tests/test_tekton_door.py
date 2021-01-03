from testing_common import tekton, load_test_data_dir
from tekton import tekton_door, tekton_system
import os
import unittest


class TestTektonDoor(unittest.TestCase):
    def test_init(self):
        test_door = tekton_door.TektonDoor()
        self.assertTrue(isinstance(test_door, tekton_door.TektonDoor))

        self.assertEqual(test_door.data_address, 0x00, "Door data address did not initialize correctly!")
        self.assertEqual(test_door.target_room_id, 0x00, "Door Target Room ID address did not initialize correctly!")
        self.assertEqual(test_door.bit_flag,
                         tekton_system.DoorBitFlag.DOOR_SAME_AREA,
                         "Door bit flag did not initialize correctly!")
        self.assertEqual(test_door.exit_direction,
                         tekton_system.DoorExitDirection.RIGHT_NO_DOOR_CLOSE,
                         "Door exit direction did not initialize correctly!")
        self.assertEqual(test_door.target_door_cap_col,
                         0x00,
                         "Door Target Door Cap Column did not initialize correctly!")
        self.assertEqual(test_door.target_door_cap_row,
                         0x00,
                         "Door Target Door Cap Row did not initialize correctly!")
        self.assertEqual(test_door.target_room_screen_h,
                         0x00,
                         "Door Target Door Cap Horizontal Screen did not initialize correctly!")
        self.assertEqual(test_door.target_room_screen_v,
                         0x00,
                         "Door Target Door Cap Vertical Screen did not initialize correctly!")
        self.assertEqual(test_door.distance_to_spawn, 0x00, "Door Distance to Spawn did not initialize correctly!")
        self.assertEqual(test_door.asm_pointer, 0x00, "Door ASM Pointer did not initialize correctly!")

    def test_bit_flag_property(self):
        test_door = tekton_door.TektonDoor()

        test_door.bit_flag = tekton_system.DoorBitFlag.DOOR_SAME_AREA
        expected_value = tekton_system.DoorBitFlag.DOOR_SAME_AREA
        self.assertEqual(expected_value, test_door.bit_flag, "Door bit flag was set incorrectly!")

        test_door.bit_flag = 0x00
        expected_value = tekton_system.DoorBitFlag.DOOR_SAME_AREA
        self.assertEqual(expected_value, test_door.bit_flag, "Door bit flag was set incorrectly!")

        with self.assertRaises(TypeError):
            test_door.bit_flag = 0.0
        with self.assertRaises(TypeError):
            test_door.bit_flag = "0"
        with self.assertRaises(ValueError):
            test_door.bit_flag = 0x15

    def test_exit_direction_property(self):
        test_door = tekton_door.TektonDoor()

        test_door.exit_direction = tekton_system.DoorExitDirection.RIGHT_NO_DOOR_CLOSE
        expected_value = tekton_system.DoorExitDirection.RIGHT_NO_DOOR_CLOSE
        self.assertEqual(expected_value, test_door.exit_direction)

        test_door.exit_direction = 0x00
        expected_value = tekton_system.DoorExitDirection.RIGHT_NO_DOOR_CLOSE
        self.assertEqual(expected_value, test_door.exit_direction)

        with self.assertRaises(TypeError):
            test_door.exit_direction = 0.0
        with self.assertRaises(TypeError):
            test_door.exit_direction = "0"
        with self.assertRaises(ValueError):
            test_door.exit_direction = 0x99

    def test_door_data_bytes(self):
        test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "fixtures",
                                     "unit",
                                     "test_tekton_door",
                                     "test_door_data_bytes",
                                     "valid_doors"
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_door = tekton_door.TektonDoor()
            test_door.data_address = test_item["data_address"]
            test_door.target_room_id = test_item["target_room_id"]
            test_door.bit_flag = test_item["bit_flag"]
            test_door.exit_direction = test_item["exit_direction"]
            test_door.target_door_cap_col = test_item["target_door_cap_col"]
            test_door.target_door_cap_row = test_item["target_door_cap_row"]
            test_door.target_room_screen_h = test_item["target_room_screen_h"]
            test_door.target_room_screen_v = test_item["target_room_screen_v"]
            test_door.distance_to_spawn = test_item["distance_to_spawn"]
            test_door.asm_pointer = test_item["asm_pointer"]
            expected_result = b''
            for el in test_item["expected_result"]:
                expected_result += el.to_bytes(1, byteorder="big")
            self.assertEqual(expected_result,
                             test_door.door_data,
                             "Door data for data address {} did not reproduce correctly!".format(
                                 test_item["data_address"]
                             )
                             )

