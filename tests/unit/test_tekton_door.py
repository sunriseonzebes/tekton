from context import tekton
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
