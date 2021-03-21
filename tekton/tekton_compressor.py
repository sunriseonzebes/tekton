"""Tekton Compressor

This module allows the user to convert a TektonTileGrid into compressed level data that the Super Metroid level loader
can understand.

Functions:
    compress_level_data: converts a TektonTileGrid into compressed level data.
"""
from .tekton_field import TektonWordFillField, TektonByteFillField, TektonDirectCopyField, TektonL1RepeaterField, \
    TektonBTSNumRepeaterField, TektonBTSNumSingleField
from .tekton_tile import TektonTile


class TektonCompressionMapper:
    """An object that converts a bytes string of uncompressed level data into compressed level data.

    Attributes:
        uncompressed_data (bytes): The string of uncompressed level data to be compressed
            (see TektonTileGrid.uncompressed_data)

    """

    def __init__(self):
        self.uncompressed_data = b''
        self._byte_map = []
        self._width_screens = 1
        self._height_screens = 1

    @property
    def width_screens(self):
        """int: Width of the room in screens"""
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
        """int: Height of the room in screens"""
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
        """bytes: The compressed version of this object's uncompressed level data"""
        self._init_byte_map()
        self._map_fields()
        compression_fields = self._generate_compression_fields()
        return_string = self.compressed_level_data_header
        return_string += self._get_bytes_string_from_compression_fields(compression_fields)
        return return_string

    @property
    def compressed_level_data_header(self):
        """bytes : The three-byte header for this level's compressed data"""
        level_header_string = b'\x01\x00'
        screen_count = self._width_screens * self._height_screens
        level_header_string += (screen_count << 1).to_bytes(1, byteorder="big")
        return level_header_string

    def _map_fields(self):
        """Maps every byte in uncompressed_data to one or more TektonField objects which each represent a different
        compression technique and can be used to generate the compressed level data. The mapping of bytes to fields is
        stored in self._byte_map

        """
        if len(self.uncompressed_data) < 1:
            return

        self._map_repeating_word_fields()
        self._map_repeating_byte_fields()
        self._map_direct_copy_fields()

    def _map_repeating_word_fields(self):
        """Searches the uncompressed level data for strings of repeating words (two bytes). Maps each string of
        repeating words to a separate TektonWordFillField object, and stores the mapping of each byte in self._byte_map.

        """
        counter = 0

        while counter < len(self.uncompressed_data) - 1:
            current_word = self.uncompressed_data[counter:counter + 2]
            if current_word[0] == current_word[1]:
                counter += 1
                continue  # Don't want a word fill field whose bytes are identical, that should be a byte fill field
            for lookahead_counter in range(counter, len(self.uncompressed_data) + 1):
                num_bytes = lookahead_counter - counter
                lookahead_byte = self.uncompressed_data[lookahead_counter:lookahead_counter + 1]
                compare_byte = current_word[num_bytes % 2:(num_bytes % 2) + 1]
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
        """Maps a single string of repeating words (two bytes) to a single TektonWordFillField object, and records which
        bytes are mapped to that field in self._bytes_map.

        Args:
            word (bytes): The word that is repeated.
            num_bytes (int): The number of bytes in the string of repeated words. This is the number of BYTES, not the
                number of times the word is repeated. Repeating the word once will have a num_bytes of 2 (one repetition
                of a word is two bytes.) This value allows odd numbers, which will only repeat the first byte of the
                last word.
            start_index (int): Index of the byte in uncompressed level data where the string of repeated words starts.

        """
        new_field = TektonWordFillField()
        new_field.num_bytes = num_bytes
        new_field.word = word
        for i in range(start_index, start_index + num_bytes):
            self._byte_map[i] = new_field

    def _map_repeating_byte_fields(self):
        """Searches the uncompressed level data for strings of repeating bytes. Maps each string of repeating bytes
        to a separate TektonByteFillField object, and stores the mapping of each byte in self._byte_map.

        """
        counter = 0

        while counter < len(self.uncompressed_data) - 1:
            current_byte = self.uncompressed_data[counter:counter + 1]
            for lookahead_counter in range(counter, len(self.uncompressed_data) + 1):
                num_bytes = lookahead_counter - counter
                lookahead_byte = self.uncompressed_data[lookahead_counter:lookahead_counter + 1]
                if current_byte != lookahead_byte or \
                        lookahead_counter == len(self.uncompressed_data) or \
                        num_bytes == 1024 or \
                        self._byte_map[lookahead_counter] is not None:
                    if num_bytes > 2:
                        self._map_repeating_byte_field(current_byte, num_bytes, counter)
                        counter = lookahead_counter
                    else:
                        counter += 1
                    break

    def _map_repeating_byte_field(self, byte, num_bytes, start_offset):
        """Maps a single string of repeating bytes to a single TektonByteFillField object, and records which bytes are
        mapped to that field in self._bytes_map.

        Args:
            bytes (bytes): The byte that is repeated.
            num_bytes (int): The number of times the byte is repeated.
            start_index (int): Index of the byte in uncompressed level data where the string of repeated bytes starts.
        """
        new_field = TektonByteFillField()
        new_field.num_bytes = num_bytes
        new_field.byte = byte
        for i in range(start_offset, start_offset + num_bytes):
            self._byte_map[i] = new_field

    def _map_direct_copy_fields(self):
        """Searches the any bytes which have not already been mapped to fields, and maps them to one or more
        TektonDirectCopyField objects.

        """
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
        """Copies a string of bytes out of uncompressed data into a TektonDirectCopyField object and and records which
        bytes are mapped to that field in self._bytes_map.

        Args:
            num_bytes (int): How many bytes to copy from uncompressed level data
            start_offset (int): Index in uncompressed level data where copying should start.

        """
        new_field = TektonDirectCopyField()
        new_field.bytes_data = self.uncompressed_data[start_offset:start_offset + num_bytes]
        for i in range(start_offset, start_offset + num_bytes):
            self._byte_map[i] = new_field

    def _init_byte_map(self):
        """Resets _byte_map to an empty state so it can be filled with mappings to TektonField objects"""
        self._byte_map = [None for i in range(len(self.uncompressed_data))]

    def _generate_compression_fields(self):
        """Creates a list of the TektonField objects in _byte_map.

        Returns:
            list: A list of TektonField objects representing the compression algorhythms that can be applied to the
                uncompressed data.

        """
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

    def _get_bytes_string_from_compression_fields(self, compression_fields):
        """Iterates over a list of TektonField objects and returns a bytes string of the compressed level data from each

        Args:
            compression_fields (list): The list of TektonField objects to iterate over.

        Returns:
            bytes: Concatenated compressed level data from all of the TektonField objects in the list.
        """
        return_string = b''
        for field in compression_fields:
            return_string += field.compressed_data

        return return_string
