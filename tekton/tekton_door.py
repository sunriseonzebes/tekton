"""Tekton Door

This module implements classes that represent doors and elevators in Super Metroid. These classes represent the data in
the ROM that stores facts about each door or elevator: what door it connects to, what direction the screen transitions
when moving through the door, how far away from the farside door should Samus spawn, etc.

This module also implements various enums to represent some door attributes that have only a few possible values, e.g.
what direction the camera should transition when passing through the door.

Classes:
    DoorBitFlag: An enum representing special instructions for rendering the mini map when passing through a door.
    DoorEjectDirection: An enum representing what direction the camera should scroll when passing through a door, and
        whether the blue door shield should close behind Samus after passing through the door.
    TektonDoor: An object representing door data for a single door in Super Metroid, including the header address of the
        farside room, what direction the camera should scroll, etc.
    TektonElevatorLaunchpad: An object representing a special kind of door that occupies the same tiles as an idle
        elevator. This special door sits in the middle of the room and doesn't trigger a screen transition like a normal
        door.

"""
from enum import Enum


class DoorBitFlag(Enum):
    """Enum representing any special instructions for the minimap when passing through a door."""
    DOOR_SAME_AREA = 0x00
    DOOR_AREA_CHANGE = 0x40
    ELEVATOR_SAME_AREA = 0x80
    ELEVATOR_AREA_CHANGE = 0xc0
    # TODO: Rename these when I figure out what they're for
    ELEVATOR_AREA_CHANGE_2 = 0Xd0
    ELEVATOR_AREA_CHANGE_3 = 0Xe0
    ELEVATOR_AREA_CHANGE_4 = 0Xf0


class DoorEjectDirection(Enum):
    """Enum representing camera scroll direction when passing through a door, and whether the blue door shield should
    close behind Samus after passing through the door."""
    RIGHT_NO_DOOR_CLOSE = 0x00
    LEFT_NO_DOOR_CLOSE = 0x01
    DOWN_NO_DOOR_CLOSE = 0x02
    UP_NO_DOOR_CLOSE = 0x03
    RIGHT = 0x04
    LEFT = 0x05
    DOWN = 0x06
    UP = 0x07


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
        self._eject_direction = DoorEjectDirection.RIGHT_NO_DOOR_CLOSE

    def __repr__(self):
        template_string = "Tekton Door:\n" + \
                          "Door Data Address: {data_address}\n" + \
                          "Target Room ID: {room_id}\n" + \
                          "Bit Flag: {bit_flag_name} ({bit_flag_value})\n" + \
                          "Eject Direction: {direction_name} ({direction_value})\n" + \
                          "Target Door Cap Coords: {door_cap_x}, {door_cap_y}\n" + \
                          "Target Room Screen Coords: {screen_x}, {screen_y}\n" + \
                          "Distance to Spawn: {dist_to_spawn}\n" + \
                          "ASM Pointer: {asm_pointer}\n"

        return template_string.format(data_address=hex(self.data_address),
                                      room_id=hex(self.target_room_id),
                                      bit_flag_name=self.bit_flag.name,
                                      bit_flag_value=hex(self.bit_flag.value),
                                      direction_name=self.eject_direction.name,
                                      direction_value=hex(self.eject_direction.value),
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
    def eject_direction(self):
        """DoorEjectDirection: Enum member representing the camera scroll direction into the target room, and whether
        this doors blue shield should close behind it."""
        return self._eject_direction

    @eject_direction.setter
    def eject_direction(self, new_eject_direction):
        if isinstance(new_eject_direction, int):
            valid_values = [item.value for item in list(DoorEjectDirection)]
            if new_eject_direction not in valid_values:
                raise ValueError("{0} is not a valid door eject direction! Valid values are: {1}".format(
                    hex(new_eject_direction),
                    ", ".join([hex(value) for value in valid_values])
                ))
            self._eject_direction = DoorEjectDirection(new_eject_direction)
        elif isinstance(new_eject_direction, DoorEjectDirection):
            self._eject_direction = new_eject_direction
        else:
            raise TypeError("Door eject direction must be int or DoorEjectDirection. "
                            "You can set a hex value using int hex notation, e.g. 0x795d4")

    @property
    def door_data(self):
        """bytes: String of bytes representing door data as it should appear in the ROM"""
        door_string = (self.target_room_id % 0x010000).to_bytes(2, byteorder="little")
        door_string += self._bit_flag.value.to_bytes(1, byteorder="little")
        door_string += self._eject_direction.value.to_bytes(1, byteorder="little")
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

