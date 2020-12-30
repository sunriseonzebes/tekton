"""Tekton Room Importer

This module implements functions which can read room data from the Super Metroid ROM and populate TektonRoom objects
with that data.

Functions:
    import_room_from_rom: Populates a TektonRoom object using the ROM contents and a level header address

"""

from .tekton_room import TektonRoom
from .tekton_system import lorom_to_pc

def import_room_from_rom(rom_contents, room_header_address):
    """Reads a room's header from ROM contents and returns a TektonRoom object populated with that room's attributes.

    Args:
        rom_contents (bytes): Byte string of ROM to import room data from
        room_header_address (int): PC address of room header data to import

    Returns:
        TektonRoom : TektonRoom object populated with data from the ROM.

    """

    if not isinstance(room_header_address, int):
        raise TypeError("Room header address must be of type int. "
                        "You can specify it in hex notation, e.g. 0x795d4")

    pointers = _get_data_addresses(rom_contents, room_header_address)

    new_room = TektonRoom()
    new_room.header = room_header_address

    new_room.width_screens = int.from_bytes(rom_contents[pointers["header"]+4:pointers["header"]+5], byteorder="big")
    new_room.height_screens = int.from_bytes(rom_contents[pointers["header"]+5:pointers["header"]+6], byteorder="big")

    # Level data addresses are stored in LoROM and are little endian
    level_lorom_address = rom_contents[pointers["standard"]+2:pointers["standard"]+5]
    new_room.level_data_address = lorom_to_pc(int.from_bytes(level_lorom_address, byteorder="little"))

    return new_room

def _get_data_addresses(rom_contents, room_header_address):
    """Reads a room's header from ROM contents and returns the PC address of certain pieces of data in the header.

    Args:
        rom_contents (bytes): Byte string of ROM to import room data from
        room_header_address (int): PC address of room header data to import

    Returns:
        dict : Dict of pc addresses for various pieces of important data, like the room's door list, standard 1 pointer
    """

    addresses = {"doors": 0,
                 "events_pointers": [],
                 "events_room_states": [],
                 "header": room_header_address,
                 "standard": room_header_address + 11}

    # Find Standard pointer
    while rom_contents[addresses["standard"]:addresses["standard"] + 2] == b"\x12\xe6":
        addresses["events_pointers"].append(addresses["standard"])
        addresses["standard"] += 5  # Room contains an events 1 pointer, skip 5 bytes to locate standard pointer
    if rom_contents[addresses["standard"]:addresses["standard"] + 2] != b'\xe6\xe5':
        unrecognized_bytes = hex(
            int.from_bytes(rom_contents[addresses["standard"]:addresses["standard"] + 2], byteorder="big")
        )
        raise ValueError(
            "Bytes {} and {} of room header data were not recognized. "
            "Expected 0x12e6 or 0xe6e5, got {}".format(hex(addresses["standard"] - room_header_address),
                                                       hex((addresses["standard"] - room_header_address) + 1),
                                                       unrecognized_bytes)
        )

    # Find beginning of doors list (technically not a pointer)
    addresses["doors"] = addresses["standard"] + 28  # Typical location of doors data is 28 bytes after standard pointer
    for i in range(len(addresses["events_pointers"])):
        addresses["events_room_states"].append(addresses["doors"])
        addresses["doors"] += 26  # For every event room state, add 26 bytes to door list address.

    return addresses




