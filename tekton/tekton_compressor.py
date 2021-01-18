"""Tekton Compressor

This module allows the user to convert a TektonTileGrid into compressed level data that the Super Metroid level loader
can understand.

Classes:
    L1RepeaterField: An object representing a series of repeating tiles in layer 1 level data

Functions:
    compress_level_data: converts a TektonTileGrid into compressed level data.
"""

from .tekton_tile import TektonTile


class L1RepeaterField:
    """An object representing a single layer 1 tile repeated a specific number of times in the level data.

    Super Metroid employs a number of "shorthand" statements to compress level data. One of the shorthands is to
    specify a tile number and it's BTS data, followed by the number of times that tile is to be repeated. This
    shorthand requires only a few bytes to represent dozens or even hundreds of tiles, and is ideal for rooms with
    large fields of the same repeated tile. This object contains all the information about the tile and the number of
    times it is repeated, and can output the compressed bytes that can be concatenated into a larger set of level data.

    L1RepeaterFields are considered fungible, and are compared by value rather than by reference. Two L1RepeaterFields
    are equivalent if they specify identical tile attributes and have the same number of repetitions.

    Attributes:
        num_reps (int): The number of times the specific tile is repeated. Super Metroid will "wrap" these tiles onto
            the next row if they exceed beyond the width of the room.
        bts_type (int): BTS type of the repeated tile.
        tileno (int): Tileset number of the repeated tile.
        h_mirror (bool): Whether or not the repeated tile should be mirrored horizontally.
        v_mirror (bool): Whether or not the repeated tile should be mirrored vertically.

    """

    def __init__(self):
        self.num_reps = 0
        self.bts_type = 0x00
        self.tileno = 0x00
        self.h_mirror = False
        self.v_mirror = False

    def __repr__(self):
        """Returns a textual representation of the RepeaterBlock.

        Returns:
            str : A textual representation of the RepeaterBlock's attributes.

        """

        template_string = "Repeater Block:\nRepetitions: {num_reps}\n Tile: {tile_repr}"
        return template_string.format(num_reps=self.num_reps,
                                      tile_repr=self.tile)

    def __eq__(self, other):
        """Determines whether two repeater blocks specify identical TektonTiles and number of repetitions.

        RepeaterBlocks are designed to be fungible. Two RepeaterBlocks are equivalent if they specify identical
        TektonTiles and if they have the same number of repetitions.

        Args:
            other: Another RepeaterBlock object for comparing to this one.

        Returns:
            bool : True if both Repeater blocks have identical TektonTiles and number of repetitions. Otherwise False.

        """

        if not isinstance(other, L1RepeaterField):
            return False
        return self.num_reps == other.num_reps and \
               self.tileno == other.tileno and \
               self.bts_type == other.bts_type and \
               self.h_mirror == other.h_mirror and \
               self.v_mirror == other.v_mirror

    @property
    def bts_tile_mirror_byte(self):
        """bytes: One byte representing tile mirror and bts data, understandable by Super Metroid's level loader."""
        byte_value = 0b00000001
        if self.h_mirror:
            byte_value += 0b100
        if self.v_mirror:
            byte_value += 0b1000
        byte_value += (self.bts_type * 0b10000)
        return byte_value.to_bytes(1, byteorder="big")

    @property
    def tile_byte(self):
        """bytes: One byte representing the tile number of this tile."""
        return self.tileno.to_bytes(1, byteorder="big")

    @property
    def compressed_data(self):
        """str: The string of bytes representing the repeated tiles in the compressed level data."""
        repeater_header = int.from_bytes(b'\xe8\x01', byteorder="big")
        repeater_header += (
                                   self.num_reps - 1) * 2  # bit shift num_repetitions one to the left. add it to the repeater header
        return_string = repeater_header.to_bytes(2, byteorder="big")
        return_string += self.tile_byte
        return_string += self.bts_tile_mirror_byte
        return return_string


def _find_blocks_for_compression(level_data):
    """Converts a TektonTileGrid into a group of objects that represent pieces of the level.

    Super Metroid employs a number of "shorthand" statements in its compressed level data. These shorthands can
    represent many tiles with only a few bytes of data, and were used to reduce the size of the level data so it would
    fit on the cartridge. This function assigns groups of tiles to "ShorthandBlock" objects, each representing part of
    the level data in a single shorthand statement. When more than one shorthand statement could be used to represent
    part of a level, this function chooses the shorthand statement requiring the fewest bytes of compressed level data.

    Args:
        level_data (TektonTileGrid): The level data to be converted into ShorthandBlocks

    Returns:
        list : A list of ShorthandBlocks containing pieces of level data

    """

    field_list = []
    counter = 1
    max_tiles = level_data.width * level_data.height

    last_tile_change = 0
    first_tile_in_field = level_data[0][0]

    while counter < max_tiles:
        current_tile = level_data[counter % level_data.width][counter // level_data.height]
        if current_tile != first_tile_in_field:
            new_field = L1RepeaterField()
            new_field.tileno = first_tile_in_field.tileno
            new_field.bts_type = first_tile_in_field.bts_type
            new_field.h_mirror = first_tile_in_field.h_mirror
            new_field.v_mirror = first_tile_in_field.v_mirror
            new_field.num_reps = counter - last_tile_change
            field_list.append(new_field)
            last_tile_change = counter
            first_tile_in_field = current_tile
        counter += 1

    # Write the last block
    new_field = L1RepeaterField()
    new_field.tile = first_tile_in_field.copy()
    new_field.num_reps = counter - last_tile_change
    field_list.append(new_field)

    return field_list


def _generate_compressed_level_data_header():
    """Generates a three-byte header that must come at the beginning of the compressed level data.

    Returns:
        bytes : The header for this level's compressed data
    """

    level_header_string = b'\x01\x00\x02'
    return level_header_string


def compress_level_data(tiles, min_string_length=0):
    """Converts a TektonTileGrid into compressed level data that Super Metroid can utilize.

    Args:
        tiles (TektonTileGrid): The level data to compress.
        min_string_length (int): The minimum length, in bytes, that the returned value should be. If the compressed
            level data is less than this size, this function pads the data with \xff bytes until it reaches this length.

    Returns:
        bytes: The string of compressed data representing the level.

    """

    compressed_level_data = b''
    level_header = _generate_compressed_level_data_header()

    compressed_level_data = level_header
    compressed_blocks = _find_blocks_for_compression(tiles)
    for block in compressed_blocks:
        compressed_level_data += block.compressed_data

    level_end_string = b'\xe4\xff\x00'

    compressed_level_data += level_end_string

    # Add FF padding to grow level data to maximum size
    while len(compressed_level_data) < min_string_length:
        compressed_level_data += b'\xff'

    return compressed_level_data
