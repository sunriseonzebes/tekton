"""Tekton Room Importer

This module implements functions which can read room data from the Super Metroid ROM and populate TektonRoom objects
with that data.

Functions:
    import_room_from_rom: Populates a TektonRoom object using the ROM contents and a level header address
    import_door: Reads door data from ROM contents and returns an object populated with the door's attributes.

"""

from .tekton_room import TektonRoom, MapArea
from .tekton_system import lorom_to_pc
from .tekton_door import TektonDoor, TektonElevatorLaunchpad, DoorBitFlag, DoorEjectDirection
from .tekton_room_state import TektonRoomState, TektonRoomEventStatePointer, TektonRoomLandingStatePointer, \
    TektonRoomFlywayStatePointer, TileSet, SongSet, SongPlayIndex
from .tekton_tile_grid import TektonTileGrid


class TektonRoomImporter:
    allowed_events_pointers = [b"\x12\xe6", b"\x69\xe6", b"\x29\xe6"]
    event_pointer_byte_lengths = {TektonRoomEventStatePointer: 5,
                                  TektonRoomLandingStatePointer: 4,
                                  TektonRoomFlywayStatePointer: 5}

    def __init__(self):
        self.rom_contents = b''
        self.room_width_screens = 1
        self.room_height_screens = 1
        self.level_data_addresses = {}

        self._room_header_address = 0

    @property
    def room_header_address(self):
        return self._room_header_address

    @room_header_address.setter
    def room_header_address(self, new_address):
        if not isinstance(new_address, int):
            raise TypeError("room_header_address must be of type int! You can use hex notation, e.g. 0x791f8")
        if new_address < 0x78000 or new_address > 0x7ffff:
            raise ValueError("room_header_address must be in LoROM bank $8F! E.g. it must have a pc address between 0x78000 and 0x7ffff")
        self._room_header_address = new_address

    def import_room_from_rom(self):
        """Reads a room's header from ROM contents and returns a TektonRoom object populated with that room's attributes.

        Returns:
            TektonRoom : TektonRoom object populated with data from the ROM.

        """

        if not isinstance(self.room_header_address, int):
            raise TypeError("Room header address must be of type int. "
                            "You can specify it in hex notation, e.g. 0x795d4")

        self.room_width_screens = self._get_int_from_rom(self.room_header_address+4, 1)
        self.room_height_screens = self._get_int_from_rom(self.room_header_address+5, 1)

        new_room = TektonRoom(self.room_width_screens, self.room_height_screens)

        new_room.header = self.room_header_address
        new_room.room_index = self._get_int_from_rom(self.room_header_address, 1)
        new_room.map_area = MapArea(self._get_int_from_rom(self.room_header_address+1, 1))
        new_room.minimap_x_coord = self._get_int_from_rom(self.room_header_address+2, 1)
        new_room.minimap_y_coord = self._get_int_from_rom(self.room_header_address+3, 1)
        new_room.up_scroller = self._get_int_from_rom(self.room_header_address+6, 1)
        new_room.down_scroller = self._get_int_from_rom(self.room_header_address+7, 1)
        new_room.special_graphics_bitflag = self._get_int_from_rom(self.room_header_address+8, 1)

        current_offset = self.room_header_address + 11
        self.level_data_addresses = {}

        while self.rom_contents[current_offset:current_offset + 2] in self.allowed_events_pointers:
            new_room_state_pointer = self._get_room_state_pointer_at_address(current_offset)
            new_room.extra_states.append(new_room_state_pointer)
            current_offset += self.event_pointer_byte_lengths[type(new_room_state_pointer)]

        if self.rom_contents[current_offset:current_offset + 2] != b'\xe6\xe5':
            raise ValueError(
                "Bytes {} and {} of room header data were not recognized. "
                "Expected one of {}, got {}".format(hex(current_offset - self.room_header_address),
                                                    hex((current_offset - self.room_header_address) + 1),
                                                    [b'\xe6\xe5'] + self.allowed_events_pointers,
                                                    self.rom_contents[current_offset:current_offset + 2])
            )

        standard_state_address = current_offset + 2
        new_room.standard_state = self._get_room_state_at_address(standard_state_address)

        for door_data_address in self._get_door_data_addresses():
            try:
                new_room.doors.append(self.import_door(door_data_address))
            except Exception as e:
                print(hex(self.room_header_address), e)
                pass

        return new_room

    def import_door(self, door_info_address):
        """Reads door data from ROM contents and returns a TektonDoor or TektonElevatorLaunchpad object populated with the
        door's attributes.

        This function will attempt to parse the 12 bytes beginning at door_info_address.

        Args:
            door_info_address (int): The PC address in rom_contents where the door data begins

        Returns:
            Mixed : TektonDoor or TektonElevatorLaunchpad object representing all the attributes of the specified door.

        """

        if not isinstance(door_info_address, int):
            raise TypeError("door_info_address must be a positive integer. "
                            "If you want to specify a hex value you can use hex notation, e.g. 0x18ac6")
        if door_info_address < 0:
            raise ValueError("door_info_address must be a positive integer.")

        door_target_room_id_bytes = self.rom_contents[door_info_address:door_info_address + 2]

        if door_target_room_id_bytes == b'\x00\x00':  # Special "doors" with no targets are used for elevators to rest on
            return self._import_elevator_launchpad(door_info_address)

        return self._import_simple_door(door_info_address)

    def _get_door_data_addresses(self):
        door_pointer_list_address = int.from_bytes(
            self.rom_contents[self.room_header_address + 9:self.room_header_address + 11],
            byteorder="little"
        )
        door_pointer_list_address += 0x70000  # Door pointer list is always in bank $8E
        door_addresses = []

        for offset in range(0, 16, 2):
            start_pos = door_pointer_list_address + offset
            end_pos = start_pos + 2
            current_door_bytes = self.rom_contents[start_pos:end_pos]
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

    def _get_room_state_pointer_at_address(self, room_state_pointer_address):
        new_state_pointer = None
        pointer_value = self.rom_contents[room_state_pointer_address: room_state_pointer_address + 2]
        if pointer_value == b'\x12\xe6':
            new_state_pointer = self._get_room_event_state_pointer_at_address(room_state_pointer_address)
        elif pointer_value == b'\x69\xe6':
            new_state_pointer = self._get_room_landing_state_pointer_at_address(room_state_pointer_address)
        elif pointer_value == b'\x29\xe6':
            new_state_pointer = self._get_room_flyway_state_pointer_at_address(room_state_pointer_address)

        return new_state_pointer

    def _get_room_event_state_pointer_at_address(self, room_state_pointer_address):
        new_event_state_pointer = TektonRoomEventStatePointer()
        new_event_state_pointer.event_value = self._get_int_from_rom(room_state_pointer_address+2, 1)
        room_state_address = self._get_int_from_rom(room_state_pointer_address+3, 2)
        room_state_address += 0x70000  # These are always in bank $8E
        new_event_state_pointer.room_state = self._get_room_state_at_address(room_state_address)

        return new_event_state_pointer

    def _get_room_landing_state_pointer_at_address(self, room_state_pointer_address):
        new_landing_state_pointer = TektonRoomLandingStatePointer()
        room_state_address = self._get_int_from_rom(room_state_pointer_address+2, 2)
        room_state_address += 0x70000  # These are always in bank $8E
        new_landing_state_pointer.room_state = self._get_room_state_at_address(room_state_address)

        return new_landing_state_pointer

    def _get_room_flyway_state_pointer_at_address(self, room_state_pointer_address):
        new_flyway_state_pointer = TektonRoomFlywayStatePointer()
        new_flyway_state_pointer.event_value = self._get_int_from_rom(room_state_pointer_address + 2, 1)
        room_state_address = self._get_int_from_rom(room_state_pointer_address + 3, 2)
        room_state_address += 0x70000  # These are always in bank $8E
        new_flyway_state_pointer.room_state = self._get_room_state_at_address(room_state_address)

        return new_flyway_state_pointer

    def _get_room_state_at_address(self, room_state_address):
        new_state = TektonRoomState()

        # Level data addresses are stored in LoROM and are little endian
        level_lorom_address = self.rom_contents[room_state_address + 0:room_state_address + 3]
        new_state.level_data_address = lorom_to_pc(level_lorom_address, byteorder="little")

        new_state.tileset = TileSet(self._get_int_from_rom(room_state_address+3, 1))
        new_state.songset = SongSet(self._get_int_from_rom(room_state_address+4, 1))
        new_state.song_play_index = SongPlayIndex(self._get_int_from_rom(room_state_address+5, 1))
        new_state.fx_pointer = self._get_int_from_rom(room_state_address+6, 2)
        new_state.enemy_set_pointer = self._get_int_from_rom(room_state_address+8, 2)
        new_state.enemy_gfx_pointer = self._get_int_from_rom(room_state_address+10, 2)
        new_state.background_x_scroll = self._get_int_from_rom(room_state_address+12, 1)
        new_state.background_y_scroll = self._get_int_from_rom(room_state_address+13, 1)
        new_state.room_scrolls_pointer = self._get_int_from_rom(room_state_address+14, 2)
        new_state.unused_pointer = self._get_int_from_rom(room_state_address+16, 2)
        new_state.main_asm_pointer = self._get_int_from_rom(room_state_address+18, 2)
        new_state.plm_set_pointer = self._get_int_from_rom(room_state_address+20, 2)
        new_state.background_pointer = self._get_int_from_rom(room_state_address+22, 2)
        new_state.setup_asm_pointer = self._get_int_from_rom(room_state_address+24, 2)

        if new_state.level_data_address in self.level_data_addresses.keys():
            new_state.tiles = self.level_data_addresses[new_state.level_data_address]
        else:
            new_state.tiles = self._get_empty_tile_data_for_room()
            self.level_data_addresses[new_state.level_data_address] = new_state.tiles

        return new_state

    def _get_empty_tile_data_for_room(self):
        new_grid = TektonTileGrid(self.room_width_screens * 16, self.room_height_screens * 16)
        new_grid.fill()
        return new_grid

    def _get_door_target_room_id(self, door_info_address):
        """Gets the header address for the farside room of a door.

        Args:
            door_info_address (int): The byte offset in the source ROM where the door's data is found.

        Returns:
            int : PC address of the farside room's level header data.

        """
        target_room_id_address = self.rom_contents[door_info_address:door_info_address + 2]
        target_room_id_address += b'\x8f'  # Super Metroid assumes all target rooms will have headers in bank $8F.
        return lorom_to_pc(target_room_id_address, byteorder="little")

    def _import_simple_door(self, door_info_address):
        """Reads door info data from the source ROM and converts it into a TektonDoor object.

        Args:
            door_info_address (int): The byte offset in the source ROM where the door's data is found.

        Returns:
            TektonDoor : Object representing all the attributes of the door data found.

        """
        new_door = TektonDoor()
        new_door.data_address = door_info_address

        door_target_room_id = self._get_door_target_room_id(door_info_address)
        new_door.target_room_id = door_target_room_id

        new_door.bit_flag = DoorBitFlag(self._get_int_from_rom(door_info_address+2, 1))
        new_door.eject_direction = DoorEjectDirection(self._get_int_from_rom(door_info_address+3, 1))
        new_door.target_door_cap_col = self._get_int_from_rom(door_info_address+4, 1)
        new_door.target_door_cap_row = self._get_int_from_rom(door_info_address+5, 1)
        new_door.target_room_screen_h = self._get_int_from_rom(door_info_address+6, 1)
        new_door.target_room_screen_v = self._get_int_from_rom(door_info_address+7, 1)
        new_door.distance_to_spawn = self._get_int_from_rom(door_info_address+8, 2)
        new_door.asm_pointer = self._get_int_from_rom(door_info_address+10, 2)

        return new_door

    def _import_elevator_launchpad(self, door_info_address):
        """Reads door info data from the source ROM and converts it into a TektonElevatorLaunchpad object.

        Args:
            door_info_address (int): The byte offset in the source ROM where the door's data is found.

        Returns:
            TektonElevatorLaunchpad : Object representing all the attributes of the door data found.

        """
        new_launchpad = TektonElevatorLaunchpad()
        new_launchpad.data_address = door_info_address
        new_launchpad.door_data = self.rom_contents[door_info_address:door_info_address + 12]
        return new_launchpad

    def _get_int_from_rom(self, start_address, num_bytes, *, byteorder="little"):
        return int.from_bytes(self.rom_contents[start_address:start_address+num_bytes], byteorder=byteorder)

