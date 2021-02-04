"""Tekton Compressor

This module allows the user to convert a TektonTileGrid into compressed level data that the Super Metroid level loader
can understand.

Functions:
    compress_level_data: converts a TektonTileGrid into compressed level data.
"""
from .tekton_field import TektonWordFillField, TektonByteFillField, TektonDirectCopyField, TektonL1RepeaterField, TektonBTSNumRepeaterField, TektonBTSNumSingleField
from .tekton_tile import TektonTile


class TektonCompressionMapper:
    def __init__(self):
        self.uncompressed_data = b''
        self._byte_map = []
        self._width_screens = 1
        self._height_screens = 1

    @property
    def width_screens(self):
        return self._width_screens

    @width_screens.setter
    def width_screens(self, new_width):
        if not isinstance(new_width, int):
            raise TypeError("width_screens must be of type int!")
        if new_width < 1:
            raise ValueError("width_screens must be 1 or greater.")
        if (new_width * self._height_screens) > 50:
            raise ValueError("Room must not contain more than 50 screens! (width_screens * height_screens <= 50)")
        self._width_screens = new_width

    @property
    def height_screens(self):
        return self._height_screens

    @height_screens.setter
    def height_screens(self, new_height):
        if not isinstance(new_height, int):
            raise TypeError("height_screens must be of type int!")
        if new_height < 1:
            raise ValueError("height_screens must be 1 or greater.")
        if (new_height * self._width_screens) > 50:
            raise ValueError("Room must not contain more than 50 screens! (width_screens * height_screens <= 50)")
        self._height_screens = new_height

    @property
    def compressed_data(self):
        self._map_fields()
        compression_fields = self._generate_compression_fields()

    @property
    def compressed_level_data_header(self):
        """bytes : The three-byte header for this level's compressed data"""

        level_header_string = b'\x01\x00'
        screen_count = self._width_screens * self._height_screens
        level_header_string += (screen_count << 1).to_bytes(1, byteorder="big")
        return level_header_string

    def _map_fields(self):
        if len(self.uncompressed_data) < 1:
            return

        self._map_repeating_word_fields()
        self._map_repeating_byte_fields()
        self._map_direct_copy_fields()

    def _map_repeating_word_fields(self):
        counter = 0
        lookahead_offset = 0

        while counter < len(self.uncompressed_data) - 1:
            current_word = self.uncompressed_data[counter:counter+2]
            if current_word[0] == current_word[1]:
                counter += 1
                continue  # Don't want a word fill field whose bytes are identical, that should be a byte fill field
            for lookahead_counter in range(counter, len(self.uncompressed_data) + 1):
                num_bytes = lookahead_counter - counter
                lookahead_byte = self.uncompressed_data[lookahead_counter:lookahead_counter+1]
                compare_byte = current_word[num_bytes%2:(num_bytes%2)+1]
                if compare_byte != lookahead_byte or \
                        lookahead_counter == len(self.uncompressed_data) or \
                        num_bytes == 1024:
                    if num_bytes > 2:
                        self._map_repeating_word_field(current_word, num_bytes, counter)
                        counter = lookahead_counter
                    else:
                        counter += 1
                    break

    def _map_repeating_word_field(self, word, num_bytes, start_index):
        new_field = TektonWordFillField()
        new_field.num_bytes = num_bytes
        new_field.word = word
        for i in range(start_index, start_index + num_bytes):
            self._byte_map[i] = new_field

    def _map_repeating_byte_fields(self):
        counter = 0
        last_byte_change_index = counter

        while counter < len(self.uncompressed_data):
            if self._byte_map[last_byte_change_index] is not None:
                counter += 1
                last_byte_change_index = counter
                continue
            current_byte = self.uncompressed_data[counter]
            last_byte_changed = self.uncompressed_data[last_byte_change_index]
            num_bytes = counter - last_byte_change_index
            if num_bytes == 1024 or current_byte != last_byte_changed or self._byte_map[counter] is not None:
                if num_bytes > 1:
                    self._map_repeating_byte_field(last_byte_changed, num_bytes, last_byte_change_index)
                last_byte_change_index = counter
            counter += 1
        last_byte_changed = self.uncompressed_data[last_byte_change_index]
        num_bytes = counter - last_byte_change_index
        if num_bytes > 1:
            self._map_repeating_byte_field(last_byte_changed, num_bytes, last_byte_change_index)

    def _map_repeating_byte_field(self, byte, num_bytes, start_offset):
        new_field = TektonByteFillField()
        new_field.num_bytes = num_bytes
        new_field.byte = byte
        for i in range(start_offset, start_offset+num_bytes):
            self._byte_map[i] = new_field

    def _map_direct_copy_fields(self):
        counter = 0
        last_unmapped_byte_index = None

        while counter < len(self.uncompressed_data):
            if last_unmapped_byte_index is not None:
                num_bytes = counter - last_unmapped_byte_index
            if self._byte_map[counter] is not None:
                if last_unmapped_byte_index is not None:
                    self._map_direct_copy_field(num_bytes, last_unmapped_byte_index)
                    last_unmapped_byte_index = None
            else:
                if last_unmapped_byte_index is None:
                    last_unmapped_byte_index = counter
                else:
                    if num_bytes > 1024:  # Max size for Field, need to split it into two fields at this point
                        self._map_direct_copy_field(num_bytes, last_unmapped_byte_index)
                        last_unmapped_byte_index = counter
            counter += 1

        if last_unmapped_byte_index is not None:
            num_bytes = counter - last_unmapped_byte_index
            self._map_direct_copy_field(num_bytes, last_unmapped_byte_index)

    def _map_direct_copy_field(self, num_bytes, start_offset):
        new_field = TektonDirectCopyField()
        new_field.bytes_data = self.uncompressed_data[start_offset:start_offset+num_bytes]
        for i in range(start_offset, start_offset+num_bytes):
            self._byte_map[i] = new_field

    def _init_byte_map(self):
        self._byte_map = [None for i in range(len(self.uncompressed_data))]



    def _generate_compression_fields(self):
        compression_fields = []
        if len(self._byte_map) < 1:
            return compression_fields
        last_field = self._byte_map[0]
        for i in range(len(self._byte_map)):
            current_field = self._byte_map[i]
            if current_field != last_field:
                compression_fields.append(last_field)
                last_field = current_field
        compression_fields.append(current_field)

        return compression_fields





def _find_layer_1_fields_for_compression(level_data):
    """Converts a TektonTileGrid into a group of objects that represent pieces of layer 1 of the level.

    Super Metroid employs a number of "shorthand" statements in its compressed level data. These shorthands can
    represent many tiles with only a few bytes of data, and were used to reduce the size of the level data so it would
    fit on the cartridge. This function assigns groups of tiles to "Field" objects, each representing part of the level
    data in a single shorthand statement. When more than one shorthand statement could be used to represent part of a
    level, this function chooses the shorthand statement requiring the fewest bytes of compressed level data.

    Args:
        level_data (TektonTileGrid): The level data to be converted into ShorthandBlocks

    Returns:
        list : A list of Field objects containing pieces of layer 1 level data

    """

    field_list = []
    counter = 1
    max_tiles = level_data.width * level_data.height

    last_tile_change = 0
    first_tile_in_field = level_data[0][0]

    while counter < max_tiles:
        current_tile = level_data[counter % level_data.width][counter // level_data.width]
        if not _tiles_layer_1_equivalent(current_tile, first_tile_in_field):
            new_field = TektonL1RepeaterField()
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
    new_field = TektonL1RepeaterField()
    new_field.tileno = first_tile_in_field.tileno
    new_field.bts_type = first_tile_in_field.bts_type
    new_field.h_mirror = first_tile_in_field.h_mirror
    new_field.v_mirror = first_tile_in_field.v_mirror
    new_field.num_reps = counter - last_tile_change
    field_list.append(new_field)

    return field_list


def _find_bts_layer_fields_for_compression(level_data):
    field_list = []
    counter = 1
    max_tiles = level_data.width * level_data.height

    last_bts_num_change = 0
    first_tile_in_field = level_data[0][0]

    while counter < max_tiles:
        current_tile = level_data[counter % level_data.width][counter // level_data.width]
        if not _tiles_bts_layer_equivalent(current_tile, first_tile_in_field):
            if (counter - last_bts_num_change) == 1:
                new_field = TektonBTSNumSingleField()
            else:
                new_field = TektonBTSNumRepeaterField()
                new_field.num_reps = counter - last_bts_num_change
            new_field.bts_num = first_tile_in_field.bts_num
            field_list.append(new_field)
            last_bts_num_change = counter
            first_tile_in_field = current_tile
        counter += 1

    # Write the last block
    new_field = TektonBTSNumRepeaterField()
    new_field.bts_num = first_tile_in_field.bts_num
    new_field.num_reps = counter - last_bts_num_change
    field_list.append(new_field)

    return field_list


def _tiles_layer_1_equivalent(left, right):
    if not isinstance(left, TektonTile) or not isinstance(right, TektonTile):
        raise TypeError("_tiles_layer_1_equivalent can only accept TektonTile objects as arguments.")

    return left.tileno == right.tileno and \
           left.bts_type == right.bts_type and \
           left.h_mirror == right.h_mirror and \
           left.v_mirror == right.v_mirror


def _tiles_bts_layer_equivalent(left, right):
    if not isinstance(left, TektonTile) or not isinstance(right, TektonTile):
        raise TypeError("_tiles_bts_layer_equivalent can only accept TektonTile objects as arguments.")

    return left.bts_num == right.bts_num


def _generate_compressed_level_data_header(room_width_screens, room_height_screens):
    """Generates a three-byte header that must come at the beginning of the compressed level data.

    Returns:
        bytes : The header for this level's compressed data
    """

    level_header_string = b'\x01\x00'
    screen_count = room_width_screens * room_height_screens
    level_header_string += (screen_count << 1).to_bytes(1, byteorder="big")
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
    level_header = _generate_compressed_level_data_header(tiles.width // 16, tiles.height // 16)

    compressed_level_data = level_header

    layer_1_fields = _find_layer_1_fields_for_compression(tiles)
    for field in layer_1_fields:
        compressed_level_data += field.compressed_data

    bts_layer_fields = _find_bts_layer_fields_for_compression(tiles)
    for field in bts_layer_fields:
        compressed_level_data += field.compressed_data

    # Add FF padding to grow level data to maximum size
    while len(compressed_level_data) < min_string_length:
        compressed_level_data += b'\xff'

    return compressed_level_data
