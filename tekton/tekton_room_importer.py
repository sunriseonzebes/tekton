"""Tekton Room Importer

This module implements functions which can read room data from the Super Metroid ROM and populate TektonRoom objects
with that data.

Functions:
    import_room_from_rom: Populates a TektonRoom object using the ROM contents and a level header address
    import_door: Reads door data from ROM contents and returns an object populated with the door's attributes.

"""

from .tekton_room import TektonRoom
from .tekton_system import lorom_to_pc
from .tekton_door import TektonDoor, TektonElevatorLaunchpad, DoorBitFlag, DoorEjectDirection
from .tekton_room_header_data import TektonRoomHeaderData, MapArea
from .tekton_room_state import TektonRoomState, TektonRoomEventStatePointer, TektonRoomSpecialStatePointer, TileSet, SongSet, SongPlayIndex


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

    room_width_screens = int.from_bytes(rom_contents[room_header_address + 4:room_header_address + 5],
                                        byteorder="big")
    room_height_screens = int.from_bytes(rom_contents[room_header_address + 5:room_header_address + 6],
                                         byteorder="big")

    new_room = TektonRoom(room_width_screens, room_height_screens)
    new_room.header = room_header_address
    new_room.header_data = _get_level_header_data(rom_contents, room_header_address)

    current_offset = room_header_address + 11
    allowed_events_pointers = [b"\x12\xe6", b"\x69\xe6", b"\x29\xe6"]
    while rom_contents[current_offset:current_offset + 2] in allowed_events_pointers:
        new_room.extra_states.append(_get_room_state_pointer_at_address(rom_contents, current_offset))
        current_offset += _get_offset_of_next_state_pointer(rom_contents[current_offset:current_offset + 2])

    if rom_contents[current_offset:current_offset + 2] != b'\xe6\xe5':
        raise ValueError(
            "Bytes {} and {} of room header data were not recognized. "
            "Expected one of {}, got {}".format(hex(current_offset - room_header_address),
                                                hex((current_offset - room_header_address) + 1),
                                                [b'\xe6\xe5'] + allowed_events_pointers,
                                                rom_contents[current_offset:current_offset + 2])
        )

    standard_state_address = current_offset + 2
    new_room.standard_state = _get_room_state_at_address(rom_contents, standard_state_address)
    new_room.level_data_address = new_room.standard_state.level_data_address

    for door_data_address in _get_door_data_addresses(rom_contents, room_header_address):
        try:
            new_room.doors.append(import_door(rom_contents, door_data_address))
        except Exception as e:
            print(hex(room_header_address), e)
            pass

    return new_room


def import_door(rom_contents, door_info_address):
    """Reads door data from ROM contents and returns a TektonDoor or TektonElevatorLaunchpad object populated with the
    door's attributes.

    This function will attempt to parse the 12 bytes beginning at door_info_address.

    Args:
        rom_contents (bytes): A bytes string of the rom contents containing the door data.
        door_info_address (int): The PC address in rom_contents where the door data begins

    Returns:
        Mixed : TektonDoor or TektonElevatorLaunchpad object representing all the attributes of the specified door.

    """

    if not isinstance(door_info_address, int):
        raise TypeError("door_info_address must be a positive integer. "
                        "If you want to specify a hex value you can use hex notation, e.g. 0x18ac6")
    if door_info_address < 0:
        raise ValueError("door_info_address must be a positive integer.")

    door_target_room_id_bytes = rom_contents[door_info_address:door_info_address + 2]

    if door_target_room_id_bytes == b'\x00\x00':  # Special "doors" with no targets are used for elevators to rest on
        return _import_elevator_launchpad(rom_contents, door_info_address)

    return _import_simple_door(rom_contents, door_info_address)


def _get_level_header_data(rom_contents, room_header_address):
    """Reads a room's header data from ROM contents and returns a TektonLevelDataHeader object that contains various
        facts about the room.

    Args:
        rom_contents (bytes): Byte string of ROM to import room header data from
        room_header_address (int): PC address of room header data to import

    """
    new_header_data = TektonRoomHeaderData()

    new_header_data.room_index = int.from_bytes(rom_contents[room_header_address:room_header_address + 1],
                                                byteorder="little")
    new_header_data.map_area = MapArea(int.from_bytes(rom_contents[room_header_address + 1:room_header_address + 2],
                                                      byteorder="little"))
    new_header_data.minimap_x_coord = int.from_bytes(rom_contents[room_header_address + 2:room_header_address + 3],
                                                     byteorder="little")
    new_header_data.minimap_y_coord = int.from_bytes(rom_contents[room_header_address + 3:room_header_address + 4],
                                                     byteorder="little")
    new_header_data.up_scroller = int.from_bytes(rom_contents[room_header_address + 6:room_header_address + 7],
                                                 byteorder="little")
    new_header_data.down_scroller = int.from_bytes(rom_contents[room_header_address + 7:room_header_address + 8],
                                                   byteorder="little")
    new_header_data.special_graphics_bitflag = int.from_bytes(rom_contents[room_header_address + 8:room_header_address + 9],
                                                              byteorder="little")

    return new_header_data


def _get_room_state_pointer_at_address(rom_contents, room_state_pointer_address):
    new_state_pointer = None
    pointer_value = rom_contents[room_state_pointer_address: room_state_pointer_address+2]
    if pointer_value == b'\x12\xe6':
        new_state_pointer = _get_room_event_state_pointer_at_address(rom_contents, room_state_pointer_address)
    elif pointer_value == b'\x69\xe6':
        new_state_pointer = _get_room_special_state_pointer_at_address(rom_contents, room_state_pointer_address)

    return new_state_pointer

def _get_room_event_state_pointer_at_address(rom_contents, room_state_pointer_address):
    new_event_state_pointer = TektonRoomEventStatePointer()
    new_event_state_pointer.event_value = int.from_bytes(
        rom_contents[room_state_pointer_address + 2:room_state_pointer_address + 3],
        byteorder="little")
    room_state_address = int.from_bytes(rom_contents[room_state_pointer_address + 3:room_state_pointer_address + 5],
                                        byteorder="little")
    room_state_address += 0x70000  # These are always in bank $8E
    new_event_state_pointer.room_state = _get_room_state_at_address(rom_contents, room_state_address)

    return new_event_state_pointer

def _get_room_special_state_pointer_at_address(rom_contents, room_state_pointer_address):
    new_special_state_pointer = TektonRoomSpecialStatePointer()
    room_state_address = int.from_bytes(rom_contents[room_state_pointer_address + 2:room_state_pointer_address + 4],
                                        byteorder="little")
    room_state_address += 0x70000  # These are always in bank $8E
    new_special_state_pointer.room_state = _get_room_state_at_address(rom_contents, room_state_address)

    return new_special_state_pointer

def _get_room_state_at_address(rom_contents, room_state_address):
    new_state = TektonRoomState()

    # Level data addresses are stored in LoROM and are little endian
    level_lorom_address = rom_contents[room_state_address + 0:room_state_address + 3]
    new_state.level_data_address = lorom_to_pc(level_lorom_address, byteorder="little")

    new_state.tileset = TileSet(int.from_bytes(rom_contents[room_state_address + 3:room_state_address + 4],
                                               byteorder="little"))
    new_state.songset = SongSet(int.from_bytes(rom_contents[room_state_address + 4:room_state_address + 5],
                                               byteorder="little"))
    new_state.song_play_index = SongPlayIndex(int.from_bytes(rom_contents[room_state_address + 5:room_state_address + 6],
                                                             byteorder="little"))
    new_state.fx_pointer = int.from_bytes(rom_contents[room_state_address + 6:room_state_address + 8],
                                          byteorder="little")
    new_state.enemy_set_pointer = int.from_bytes(rom_contents[room_state_address + 8:room_state_address + 10],
                                                 byteorder="little")
    new_state.enemy_gfx_pointer = int.from_bytes(rom_contents[room_state_address + 10:room_state_address + 12],
                                                 byteorder="little")
    new_state.background_x_scroll = int.from_bytes(rom_contents[room_state_address + 12:room_state_address + 13],
                                                   byteorder="little")
    new_state.background_y_scroll = int.from_bytes(rom_contents[room_state_address + 13:room_state_address + 14],
                                                   byteorder="little")
    new_state.room_scrolls_pointer = int.from_bytes(rom_contents[room_state_address + 14:room_state_address + 16],
                                                    byteorder="little")
    new_state.unused_pointer = int.from_bytes(rom_contents[room_state_address + 16:room_state_address + 18],
                                              byteorder="little")
    new_state.main_asm_pointer = int.from_bytes(rom_contents[room_state_address + 18:room_state_address + 20],
                                                byteorder="little")
    new_state.plm_set_pointer = int.from_bytes(rom_contents[room_state_address + 20:room_state_address + 22],
                                               byteorder="little")
    new_state.background_pointer = int.from_bytes(rom_contents[room_state_address + 22:room_state_address + 24],
                                                  byteorder="little")
    new_state.setup_asm_pointer = int.from_bytes(rom_contents[room_state_address + 24:room_state_address + 26],
                                                 byteorder="little")

    return new_state

def _get_offset_of_next_state_pointer(current_state_pointer):
    if current_state_pointer == b'\x12\xe6':
        return 5
    elif current_state_pointer == b'\x69\xe6':
        return 4


def _get_door_data_addresses(rom_contents, room_header_address):
    door_pointer_list_address = int.from_bytes(rom_contents[room_header_address + 9:room_header_address + 11],
                                       byteorder="little")
    door_pointer_list_address += 0x70000  # Door pointer list is always in bank $8E
    door_addresses = []

    for offset in range(0, 16, 2):
        start_pos = door_pointer_list_address + offset
        end_pos = door_pointer_list_address + offset + 2
        current_door_bytes = rom_contents[start_pos:end_pos]
        if current_door_bytes == b'\x00\x00':
            break
        current_door_bytes += b'\x83'  # Super Metroid assumes all door data lives in bank $83.
        try:
            pc_door_data_address = lorom_to_pc(current_door_bytes, byteorder="little")
        except ValueError:
            break
        except Exception as e:
            raise e
        door_addresses.append(pc_door_data_address)

    return door_addresses


def _get_door_target_room_id(rom_contents, door_info_address):
    """Gets the header address for the farside room of a door.

    Args:
        rom_contents (bytes): The contents of the source ROM
        door_info_address (int): The byte offset in the source ROM where the door's data is found.

    Returns:
        int : PC address of the farside room's level header data.

    """
    target_room_id_address = rom_contents[door_info_address:door_info_address + 2]
    target_room_id_address += b'\x8f'  # Super Metroid assumes all target rooms will have headers in bank $8F.
    return lorom_to_pc(target_room_id_address, byteorder="little")


def _import_simple_door(rom_contents, door_info_address):
    """Reads door info data from the source ROM and converts it into a TektonDoor object.

    Args:
        rom_contents (bytes): The contents of the source ROM
        door_info_address (int): The byte offset in the source ROM where the door's data is found.

    Returns:
        TektonDoor : Object representing all the attributes of the door data found.

    """
    new_door = TektonDoor()
    new_door.data_address = door_info_address

    door_target_room_id = _get_door_target_room_id(rom_contents, door_info_address)
    new_door.target_room_id = door_target_room_id

    new_door.bit_flag = DoorBitFlag(
        int.from_bytes(rom_contents[door_info_address + 2:door_info_address + 3], byteorder="little")
    )
    new_door.eject_direction = DoorEjectDirection(
        int.from_bytes(rom_contents[door_info_address + 3:door_info_address + 4], byteorder="little")
    )
    new_door.target_door_cap_col = int.from_bytes(
        rom_contents[door_info_address + 4:door_info_address + 5],
        byteorder="little"
    )
    new_door.target_door_cap_row = int.from_bytes(
        rom_contents[door_info_address + 5:door_info_address + 6],
        byteorder="little"
    )
    new_door.target_room_screen_h = int.from_bytes(
        rom_contents[door_info_address + 6:door_info_address + 7],
        byteorder="little"
    )
    new_door.target_room_screen_v = int.from_bytes(
        rom_contents[door_info_address + 7:door_info_address + 8],
        byteorder="little"
    )
    new_door.distance_to_spawn = int.from_bytes(
        rom_contents[door_info_address + 8:door_info_address + 10],
        byteorder="little"
    )
    new_door.asm_pointer = int.from_bytes(
        rom_contents[door_info_address + 10:door_info_address + 12],
        byteorder="little"
    )
    return new_door


def _import_elevator_launchpad(rom_contents, door_info_address):
    """Reads door info data from the source ROM and converts it into a TektonElevatorLaunchpad object.

    Args:
        rom_contents (bytes): The contents of the source ROM
        door_info_address (int): The byte offset in the source ROM where the door's data is found.

    Returns:
        TektonElevatorLaunchpad : Object representing all the attributes of the door data found.

    """
    new_launchpad = TektonElevatorLaunchpad()
    new_launchpad.data_address = door_info_address
    new_launchpad.door_data = rom_contents[door_info_address:door_info_address + 12]
    return new_launchpad
