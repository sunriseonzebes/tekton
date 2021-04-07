"""Tekton Room

This module implements the TektonRoom class, an object which abstracts many different attributes of a room in Super
Metroid. It also implements associated exceptions for use with this class.

Classes:
    TektonRoom: An object containing many different attributes of a Super Metroid room. It can output the room as a
        stream of compressed data which can be inserted into the ROM.
    CompressedDataTooLargeError: An exception raised when a TektonRoom's compressed level data is too large.

"""

from enum import Enum
from .tekton_tile import TektonTile
from .tekton_tile_grid import TektonTileGrid
from .tekton_compressor import TektonCompressionMapper
from .tekton_system import pad_bytes, pc_to_lorom
from .tekton_room_state import TektonRoomState, TektonRoomLandingStatePointer


class MapArea(Enum):
    """Enumeration that lists out the different regions of the planet."""
    CRATERIA = 0x00
    BRINSTAR = 0x01
    NORFAIR = 0x02
    WRECKED_SHIP = 0x03
    MARIDIA = 0x04
    TOURIAN = 0x05
    CERES = 0x06
    DEBUG = 0x07


class TektonRoom:
    """An object representing a single room in Super Metroid, with many different modifiable attributes.

    Attributes:
        doors (list): List of TektonDoors objects representing the doors in the room
        height_screens (int): The height (in screens) of the room. One screen is 16 tiles.
        level_data_length (int): The maximum length in bytes of this room's compressed level data.
        name (str): The nickname for this room. (This data is not copied to the ROM.)
        tiles (TektonTileGrid): An object containing a two-dimensional matrix of the tiles in this room.
        width_screens (int): The width (in screens) of the room. One screen is 16 tiles.
        write_level_data (bool): If True, writes data in tiles to modified ROM. If False, does not modify level data.

    """

    def __init__(self, width=1, height=1):
        self.doors = []
        self.down_scroller = 0
        self.extra_states = []
        self.height_screens = height
        self.level_data_length = 0
        self.map_area = MapArea.CRATERIA
        self.minimap_x_coord = 0
        self.minimap_y_coord = 0
        self.name = None
        self.room_index = 0
        self.special_graphics_bitflag = 0
        self.standard_state = TektonRoomState()
        self.up_scroller = 0
        self.width_screens = width
        self.write_level_data = True

        self._header = 0x00

    @property
    def header(self):
        """int: Get or set the PC address in the ROM where this room's header data can be found."""
        return self._header

    @header.setter
    def header(self, new_header):
        if not isinstance(new_header, int):
            raise TypeError(
                "Room header address must be of type int. You can set a hex value using int hex notation, e.g. 0x795d4"
            )
        if new_header < 0:
            raise ValueError("Room header address must be a positive number.")
        self._header = new_header

    @property
    def tiles(self):
        raise ValueError("This attribute has been removed.")

    @property
    def header_data(self):
        header_bytes = self.room_index.to_bytes(1, byteorder="little")
        header_bytes += self.map_area.value.to_bytes(1, byteorder="little")
        header_bytes += self.minimap_x_coord.to_bytes(1, byteorder="little")
        header_bytes += self.minimap_y_coord.to_bytes(1, byteorder="little")
        header_bytes += self.width_screens.to_bytes(1, byteorder="little")
        header_bytes += self.height_screens.to_bytes(1, byteorder="little")
        header_bytes += self.up_scroller.to_bytes(1, byteorder="little")
        header_bytes += self.down_scroller.to_bytes(1, byteorder="little")
        header_bytes += self.special_graphics_bitflag.to_bytes(1, byteorder="little")
        header_bytes += (self._get_door_pointer_list_address() % 0x10000).to_bytes(2, byteorder="little")


        for room_state_pointer in self.extra_states:
            header_bytes += room_state_pointer.pointer_code
            if not isinstance(room_state_pointer, TektonRoomLandingStatePointer):
                header_bytes += room_state_pointer.event_value.to_bytes(1, byteorder="little")
            header_bytes += (self._get_room_state_address(room_state_pointer) % 0x10000).to_bytes(2, byteorder="little")

        header_bytes += b'\xe6\xe5'
        header_bytes += self._get_room_state_header_data(self.standard_state)

        for room_state_pointer in self.extra_states:
            header_bytes += self._get_room_state_header_data(room_state_pointer.room_state)



        for door in self.doors:
            header_bytes += (door.data_address % 0x10000).to_bytes(2, byteorder="little")

        return header_bytes

    def compressed_level_data(self, room_state):
        """Returns compressed level data which the Super Metroid ROM can understand.

        Returns:
            bytes : The string of compressed level data representing the room's tiles.

        """
        compressor = TektonCompressionMapper()
        compressor.width_screens = self.width_screens
        compressor.height_screens = self.height_screens
        compressor.uncompressed_data = room_state.tiles.uncompressed_data
        compressed_data = compressor.compressed_data
        if 0 < self.level_data_length < len(compressed_data):
            raise CompressedDataTooLargeError(
                "Compressed data is {0} bytes, but max size is {1} bytes!".format(len(compressed_data),
                                                                                  self.level_data_length))
        return pad_bytes(compressed_data, self.level_data_length, b'\xff')

    def _get_room_state_pointers_list_length(self):
        room_state_pointers_length = 0
        for room_state_pointer in self.extra_states:
            if isinstance(room_state_pointer, TektonRoomLandingStatePointer):
                room_state_pointers_length += 4
            else:
                room_state_pointers_length += 5

        return room_state_pointers_length

    def _get_room_state_address(self, room_state_pointer):
        state_pointer_number = 0
        for i in range(len(self.extra_states)):
            if self.extra_states[i] == room_state_pointer:
                state_pointer_number = i
                break;

        return self.header + 11 + self._get_room_state_pointers_list_length() + 28 + ((state_pointer_number) * 26)

    def _get_door_pointer_list_address(self):
        return self.header + 11 + self._get_room_state_pointers_list_length() + 28 + (len(self.extra_states) * 26)

    def _get_room_state_header_data(self, room_state):
        room_state_header_data = pc_to_lorom(room_state.level_data_address, byteorder="little")
        room_state_header_data += room_state.tileset.value.to_bytes(1, byteorder="little")
        room_state_header_data += room_state.songset.value.to_bytes(1, byteorder="little")
        room_state_header_data += room_state.song_play_index.value.to_bytes(1, byteorder="little")
        room_state_header_data += room_state.fx_pointer.to_bytes(2, byteorder="little")
        room_state_header_data += room_state.enemy_set_pointer.to_bytes(2, byteorder="little")
        room_state_header_data += room_state.enemy_gfx_pointer.to_bytes(2, byteorder="little")
        room_state_header_data += room_state.background_x_scroll.to_bytes(1, byteorder="little")
        room_state_header_data += room_state.background_y_scroll.to_bytes(1, byteorder="little")
        room_state_header_data += room_state.room_scrolls_pointer.to_bytes(2, byteorder="little")
        room_state_header_data += room_state.unused_pointer.to_bytes(2, byteorder="little")
        room_state_header_data += room_state.main_asm_pointer.to_bytes(2, byteorder="little")
        room_state_header_data += room_state.plm_set_pointer.to_bytes(2, byteorder="little")
        room_state_header_data += room_state.background_pointer.to_bytes(2, byteorder="little")
        room_state_header_data += room_state.setup_asm_pointer.to_bytes(2, byteorder="little")

        return room_state_header_data


class CompressedDataTooLargeError(Exception):
    """Exception returned when the compressed level data exceeds the maximum allowable size for the room."""
    pass
