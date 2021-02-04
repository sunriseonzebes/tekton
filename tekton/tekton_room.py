"""Tekton Room

This module implements the TektonRoom class, an object which abstracts many different attributes of a room in Super
Metroid. It also implements associated exceptions for use with this class.

Classes:
    TektonRoom: An object containing many different attributes of a Super Metroid room. It can output the room as a
        stream of compressed data which can be inserted into the ROM.
    CompressedDataTooLargeError: An exception raised when a TektonRoom's compressed level data is too large.

"""

from .tekton_tile import TektonTile
from .tekton_tile_grid import TektonTileGrid
from .tekton_compressor import TektonCompressionMapper
from .tekton_system import pad_bytes

class TektonRoom:
    """An object representing a single room in Super Metroid, with many different modifiable attributes.

    Attributes:
        doors (list): List of TektonDoors objects representing the doors in the room
        height_screens (int): The height (in screens) of the room. One screen is 16 tiles.
        level_data_length (int): The maximum length in bytes of this room's compressed level data.
        name (str): The nickname for this room. (This data is not copied to the ROM.)
        tiles (TektonTileGrid): An object containing a two-dimensional matrix of the tiles in this room.
        width_screens (int): The width (in screens) of the room. One screen is 16 tiles.

    """
    def __init__(self, width=1, height=1):
        self.doors = []
        self.height_screens = height
        self.level_data_length = 0
        self.name = None
        self.tiles = TektonTileGrid(width * 16, height * 16)
        self.tiles.fill()
        self.width_screens = width

        self._header = 0x00
        self._level_data_address = 0x00

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
    def level_data_address(self):
        """int: Get or set the PC address in the ROM where this room's level data can be found."""
        return self._level_data_address

    @level_data_address.setter
    def level_data_address(self, new_address):
        if not isinstance(new_address, int):
            raise TypeError(
                "Room level data address must be of type int. "
                "You can set a hex value using int hex notation, e.g. 0x21bcd2"
            )
        if new_address < 0:
            raise ValueError("Room level data address must be a positive number.")
        self._level_data_address = new_address


    def compressed_level_data(self):
        """Returns compressed level data which the Super Metroid ROM can understand.

        Returns:
            bytes : The string of compressed level data representing the room's tiles.

        """
        compressor = TektonCompressionMapper()
        compressor.width_screens = self.width_screens
        compressor.height_screens = self.height_screens
        compressor.uncompressed_data = self.tiles.uncompressed_data
        compressed_data = compressor.compressed_data
        if len(compressed_data) > self.level_data_length:
            raise CompressedDataTooLargeError("Compressed data is {0} bytes, but max size is {1} bytes!".format(len(compressed_data),
                                                                                                                self.level_data_length))
        return pad_bytes(compressed_data, self.level_data_length, b'\xff')


class CompressedDataTooLargeError(Exception):
    """Exception returned when the compressed level data exceeds the maximum allowable size for the room."""
    pass