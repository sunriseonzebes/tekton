from .tekton_system import DoorBitFlag, DoorExitDirection


class TektonDoor:
    def __init__(self):
        self.data_address = 0x00
        self.target_room_id = 0x00
        self.bit_flag = DoorBitFlag.DOOR_SAME_AREA
        self.exit_direction = DoorExitDirection.RIGHT_NO_DOOR_CLOSE
        self.target_door_cap_col = 0x00
        self.target_door_cap_row = 0x00
        self.target_room_screen_h = 0x00
        self.target_room_screen_v = 0x00
        self.distance_to_spawn = 0x00
        self.asm_pointer = 0x00
