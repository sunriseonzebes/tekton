from .tekton_system import DoorBitFlag, DoorExitDirection


class TektonDoor:  # TODO: Probably make a superclass of Door and Launchpad
    """An object representing a single door in Super Metroid, with many modifiable attributes.

    Attributes:
        data_address (int): The PC address where the door data for this door can be found in the ROM.
        target_room_id (int): The PC address of the room header for the room that this door leads to.
        target_door_cap_col (int): X coord, in tiles, in the target room of where this door's cap should be drawn after
            Samus passes through this door.
        target_door_cap_col (int): Y coord, in tiles, in the target room of where this door's cap should be drawn after
            Samus passes through this door.
        target_room_screen_h (int): Screen number X coord (starts at 0) in the target room where Samus should appear
            after passing through this door.
        target_room_screen_v (int): Screen number Y coord (starts at 0) in the target room where Samus should appear
            after passing through this door.
        distance_to_spawn (int): How far from the door Samus should appear after passing through it.
        asm_pointer (int): PC address of special instructions to execute after Samus passes through this door.

    """

    def __init__(self):
        self.data_address = 0x00
        self.target_room_id = 0x00
        self.target_door_cap_col = 0x00
        self.target_door_cap_row = 0x00
        self.target_room_screen_h = 0x00
        self.target_room_screen_v = 0x00
        self.distance_to_spawn = 0x00
        self.asm_pointer = 0x00

        self._bit_flag = DoorBitFlag.DOOR_SAME_AREA
        self._exit_direction = DoorExitDirection.RIGHT_NO_DOOR_CLOSE

    def __repr__(self):
        template_string = "Tekton Door:\n" + \
                          "Door Data Address: {data_address}\n" + \
                          "Target Room ID: {room_id}\n" + \
                          "Bit Flag: {bit_flag_name} ({bit_flag_value})\n" + \
                          "Exit Direction: {direction_name} ({direction_value})\n" + \
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

    @property
    def bit_flag(self):
        """DoorBitFlag: Enum member representing this door's bit flag."""
        return self._bit_flag

    @bit_flag.setter
    def bit_flag(self, new_bit_flag):
        if isinstance(new_bit_flag, int):
            valid_values = [item.value for item in list(DoorBitFlag)]
            if new_bit_flag not in valid_values:
                raise ValueError("{0} is not a valid door bit flag value! Valid values are: {1}".format(
                    hex(new_bit_flag),
                    ", ".join([hex(value) for value in valid_values])
                ))
            self._bit_flag = DoorBitFlag(new_bit_flag)
        elif isinstance(new_bit_flag, DoorBitFlag):
            self._bit_flag = new_bit_flag
        else:
            raise TypeError("Door bitflag must be int or DoorBitFlag. "
                            "You can set a hex value using int hex notation, e.g. 0x795d4")

    @property
    def exit_direction(self):
        """DoorExitDirection: Enum member representing this door's exit direction into the target room, and whether its
        door cap should close behind it."""
        return self._exit_direction

    @exit_direction.setter
    def exit_direction(self, new_exit_direction):
        if isinstance(new_exit_direction, int):
            valid_values = [item.value for item in list(DoorExitDirection)]
            if new_exit_direction not in valid_values:
                raise ValueError("{0} is not a valid door exit direction! Valid values are: {1}".format(
                    hex(new_exit_direction),
                    ", ".join([hex(value) for value in valid_values])
                ))
            self._exit_direction = DoorExitDirection(new_exit_direction)
        elif isinstance(new_exit_direction, DoorExitDirection):
            self._exit_direction = new_exit_direction
        else:
            raise TypeError("Door exit direction must be int or DoorExitDirection. "
                            "You can set a hex value using int hex notation, e.g. 0x795d4")

    @property
    def door_data(self):
        """bytes: String of bytes representing door data as it should appear in the ROM"""
        door_string = (self.target_room_id % 0x010000).to_bytes(2, byteorder="little")
        door_string += self._bit_flag.value.to_bytes(1, byteorder="little")
        door_string += self._exit_direction.value.to_bytes(1, byteorder="little")
        door_string += self.target_door_cap_col.to_bytes(1, byteorder="little")
        door_string += self.target_door_cap_row.to_bytes(1, byteorder="little")
        door_string += self.target_room_screen_h.to_bytes(1, byteorder="little")
        door_string += self.target_room_screen_v.to_bytes(1, byteorder="little")
        door_string += self.distance_to_spawn.to_bytes(2, byteorder="little")
        door_string += self.asm_pointer.to_bytes(2, byteorder="little")

        return door_string


class TektonElevatorLaunchpad:
    """Implements a special kind of door which occupies a door slot, but serves as a platform where Samus can stand to
    activate an elevator. Has no configurable attributes.

    Atrtibutes:
        data_address (int): The PC address where the door data for this door can be found in the ROM.
        door_data (bytes): The meaning of the door data is not currently understood, so the bytes are copied exactly.

    """

    def __init__(self):
        self.data_address = 0x00
        self._door_data = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    @property
    def door_data(self):
        """bytes: Twelve-byte sequence of raw door data from the ROM."""
        return self._door_data

    @door_data.setter
    def door_data(self, new_value):
        if not isinstance(new_value, bytes):
            raise TypeError("Elevator Launchpad door data must be of type bytes!")
        if len(new_value) != 12:
            raise ValueError("Elevator Launchpad door data must be twelve bytes long!")
        self._door_data = new_value