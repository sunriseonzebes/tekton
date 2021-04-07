"""Tekton System

This module implements utility classes and functions that various other modules can use.

Functions:
    lorom_to_pc: Converts a LoROM address to a PC address
    overwrite_bytes_at_index: Replaces bytes in an input string with a new string of bytes

"""


def lorom_to_pc(lorom_string, *, byteorder):
    """Converts SNES LoROM addresses into normal PC hex addresses.

    SNES addresses are often specified in LoROM values, however python requires a normal integer offset (a "pc address")
    to find objects in a bytes stream. Super Metroid specifies som addresses in LoROM (such as the level data address
    in a room header,) this address would need to be converted into a pc address to use it as an offset in a bytes
    string containing the ROM data.

    The most significant byte of a LoROM address is called the "bank." Certain LoROM addresses are invalid, for example
    the address $80:9999 would be outside the range of allowable addresses for bank $80, which stops at $80:7fff.
    In the event of an invalid address, Super Metroid apparently ignores any bits larger than the maximum size of the
    bank. In this case, the most significant bit in 9999 would be ignored, causing the address to resolve to $80:1999, a
    valid address. There are a number of invalid addresses in room headers which seem to expect this capability. This
    function will do the same when it encounters an invalid address.

    Args:
        lorom_string (bytes): Bytes string containing the LoROM address.
        byteorder (str): Byte order (endianess) of lorom_string. Must be "little" or "big".

    Returns:
        int : PC address of lorom_string

    """

    if byteorder not in ["little", "big"]:
        return ValueError("byteorder must be one of \"little\", \"big\"")
    if not isinstance(lorom_string, bytes):
        raise TypeError("LoROM value must be of type bytes.")
    lorom_value_int = int.from_bytes(lorom_string, byteorder=byteorder)
    if lorom_value_int < 0x800000 or lorom_value_int > 0xffffff:
        raise ValueError(
            "LoROM value must be a positive number between 0x800000 and 0xffffff"
        )
    lorom_bank = lorom_value_int // 0x010000  # Bank number is the largest byte of the lorom value
    lorom_address = lorom_value_int % 0x008000  # 0100 0000 0000 0000 address is the smallest 15 bits of the lorom value
    # If the bank number is odd, the largest bit of the address should be a 1
    if lorom_bank % 2 == 1:
        lorom_address += 0x8000  # 1000 0000 0000 0000

    pc_value = (((lorom_bank - 0x80) // 2) * 0x010000) + lorom_address
    return pc_value

def pc_to_lorom(pc_address, *, byteorder):
    lorom_address = pc_address % 0x010000
    lorom_bank = ((pc_address // 0x008000) + 0x80) * 0x10000

    return (lorom_bank + lorom_address).to_bytes(3, byteorder=byteorder)



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


def pad_bytes(input_string, min_length, pad_byte):
    """Appends bytes to the end of a input_string to ensure it contains at least min_length bytes. Does not modify the
    string if it is already longer than min_length.

    Args:
        input_string (bytes): The input string to pad with bytes, if necessary
        min_length (int): The minimum length input_string should be
        pad_byte (byte): The byte value used to pad input_string, if necessary

    Returns:
        bytes : input_string if it is already longer than min_length, otherwise returns input_string padded with bytes
            to make it min_length bytes long.

    """
    return_string = input_string
    while len(return_string) < min_length:
        return_string += pad_byte
    return return_string
