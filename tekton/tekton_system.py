"""Tekton System

This module implements utility classes and functions that various other modules can use.

Functions:
    lorom_to_pc: Converts a LoROM address to a PC address
    overwrite_bytes_at_index: Replaces bytes in an input string with a new string of bytes

"""

from enum import Enum

class DoorBitFlag(Enum):
    DOOR_SAME_AREA = 0x00,
    DOOR_AREA_CHANGE = 0x40,
    ELEVATOR_SAME_AREA = 0x80,
    ELEVATOR_AREA_CHANGE = 0xc0

class DoorExitDirection(Enum):
    RIGHT_NO_DOOR_CLOSE = 0x00,
    LEFT_NO_DOOR_CLOSE = 0x01,
    DOWN_NO_DOOR_CLOSE = 0x02,
    UP_NO_DOOR_CLOSE = 0x03,
    RIGHT = 0x04,
    LEFT = 0x05,
    DOWN = 0x06,
    UP = 0x07


def lorom_to_pc(lorom_value_int):
    if not isinstance(lorom_value_int, int):
        raise TypeError(
            "LoROM value must be of type int. "
            "You can specify this number using int hex notation, e.g. 0xc3bcd2"
        )
    if lorom_value_int < 0 or lorom_value_int > 0xffffff:
        raise ValueError(
            "LoROM value must be a positive number less than or equal to 0xffffff"
        )
    lorom_bank = lorom_value_int // 0x010000
    lorom_address = lorom_value_int % 0x010000
    pc_value = (((lorom_bank - 0x80) // 2) * 0x010000) + lorom_address
    return pc_value


def overwrite_bytes_at_index(original_string, replace_string, replace_start_index):
    """Replaces bytes in a string with a different string, starting at a specific index.

    This can be used to overwrite a section of a ROM with a new byte string. This function does not insert the bytes
    at the specified index, instead it replaces existing bytes starting at the specified index.

    Args:
        original_string (bytes): The original string of bytes
        replace_string (bytes): The string of bytes used to overwrite the original string
        replace_start_index (int): The index of the original string where the overwrite should start

    Returns:
        bytes : The finalized bytes string with the specified bytes overwritten by the replacement string

    """
    output_string = original_string[0:replace_start_index]
    output_string += replace_string
    replace_end_index = replace_start_index + len(replace_string)
    output_string += original_string[replace_end_index:]

    return output_string
