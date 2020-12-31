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

    def __repr__(self):
        template_string = "Tekton Door:\n" + \
                          "Door Data Address: {data_address}\n" + \
                          "Target Room ID: {room_id}\n" + \
                          "Bit Flag: {bit_flag_name}({bit_flag_value})\n" + \
                          "Exit Direction: {direction_name}({direction_value})\n" + \
                          "Target Door Cap Coords: {door_cap_x}, {door_cap_y}\n" + \
                          "Target Room Screen Coords: {screen_x}, {screen_y}\n" + \
                          "Distance to Spawn: {dist_to_spawn}\n" + \
                          "ASM Pointer: {asm_pointer}\n"

        return template_string.format(data_address=hex(self.data_address),
                                      room_id=hex(self.target_room_id),
                                      bit_flag_name=self.bit_flag.name,
                                      bit_flag_value=hex(self.bit_flag.value),
                                      direction_name=self.exit_direction.name,
                                      direction_value=hex(self.exit_direction.value),
                                      door_cap_x=hex(self.target_door_cap_col),
                                      door_cap_y=hex(self.target_door_cap_row),
                                      screen_x=hex(self.target_room_screen_h),
                                      screen_y=hex(self.target_room_screen_v),
                                      dist_to_spawn=hex(self.distance_to_spawn),
                                      asm_pointer=hex(self.asm_pointer)
                                      )

    def __str__(self):
        return self.__repr__()
