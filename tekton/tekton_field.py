"""Tekton Field

This module implements a various classes that represent compression algorithm techniques used by Super Metroid to
compress level data. Each class represents a single technique or method of compressing data. These classes are used by
the TektonCompressor class to represent uncompressed level data as a series of "fields" that can be compressed with a
specific algorithm. Each chunk can output a string of compressed data, which can be concatenated to represent the
complete compressed data for an entire room.

Classes:
    TektonField: Superclass for the different kinds of compression algorithms Super Metroid can use.
    TektonDirectCopyField: Field that contains data that was too complicated to be compressed, and must be represented
        in uncompressed form.
    TektonByteFillField: Field that represents a single byte repeated a number of times.
    TektonWordFillField: Field that represents a single word (two bytes) repeated for a number of bytes (allows an odd
        number of bytes which will split the final word in half.)

"""


class TektonField:
    """Superclass of other "Field" objects which defines common behavior between them.

    Class Attributes:
        command_code: Three-bit number representing which compression "instruction" is used by this field. Each type of
            algorithm has a unique three-bit command code.
        extended_command_code: Three-bit number prepended to the command code when this field represents more than 33
            bytes of data.

    """
    command_code = 0b000
    extended_command_code = 0b111

    def __init__(self):
        self._num_bytes = 1

    @property
    def num_bytes(self):
        """int: Number of bytes produced by this field."""
        return self._num_bytes

    @num_bytes.setter
    def num_bytes(self, new_value):
        if not isinstance(new_value, int):
            raise TypeError("num_bytes must be int! You may use hex notation if you like, e.g. 0xa2")
        if new_value < 1 or new_value > 1024:
            raise ValueError("num_bytes must be between 1 and 1024! You may use hex notation if you like, e.g. 0xa2")
        self._num_bytes = new_value

    @property
    def cmd_and_reps_bytes(self):
        """bytes: One- or two-byte sequence which contains the command code followed by the number of bytes produced by
        this field. When num_bytes is less than 33, this returns a single byte, consisting of the three-bit command code
        followed by the five-bit number of bytes. If num_bytes is 33 or greater, this returns two bytes, consisting of
        a three-bit extended command code, a three bit command code, and a ten-bit number of bytes."""
        if self._num_bytes < 32:
            return_value = self.command_code << 5
            return_value += (self._num_bytes - 1)
            return return_value.to_bytes(1, byteorder="big")
        else:
            return_value = self.extended_command_code << 13
            return_value += (self.command_code << 10)
            return_value += (self._num_bytes - 1)
            return return_value.to_bytes(2, byteorder="big")

    @property
    def compressed_data(self):
        """bytes: A string of compressed level data that Super Metroid can understand."""
        pass


class TektonDirectCopyField(TektonField):
    command_code = 0b000

    def __init__(self):
        super(TektonDirectCopyField, self).__init__()
        self._bytes_data = b'\x00'

    @property
    def bytes_data(self):
        return self._bytes_data

    @bytes_data.setter
    def bytes_data(self, new_bytes_data):
        if not isinstance(new_bytes_data, (int, bytes)):
            raise TypeError("bytes_data must be of type bytes or int. You may use hex notation, e.g. 0xfa")
        if isinstance(new_bytes_data, int):
            if new_bytes_data < 0:
                raise ValueError("bytes_data must be a positive integer!")
            new_bytes_data = new_bytes_data.to_bytes((new_bytes_data.bit_length() // 8) + 1, byteorder="big")
        elif isinstance(new_bytes_data, bytes):
            if len(new_bytes_data) < 1:
                raise ValueError("bytes_data must contain at least one byte!")
        self._bytes_data = new_bytes_data
        self._num_bytes = len(self._bytes_data)

    @property
    def compressed_data(self):
        return_string = self.cmd_and_reps_bytes
        return_string += self._bytes_data

        return return_string


class TektonByteFillField(TektonField):
    command_code = 0b001

    def __init__(self):
        super(TektonByteFillField, self).__init__()
        self._byte = b'\x00'

    @property
    def byte(self):
        """bytes: Returns the byte value which this field is filled with."""
        return self._byte

    @byte.setter
    def byte(self, new_byte):
        if not isinstance(new_byte, (int, bytes)):
            raise TypeError("byte property must be of type int or bytes! You may use hex notation, e.g. 0x1f")
        if isinstance(new_byte, int):
            if new_byte < 0 or new_byte > 255:
                raise ValueError("byte value must be between 0 and 255 (0x00 and 0xff)")
            new_byte = new_byte.to_bytes(1, byteorder="big")
        elif isinstance(new_byte, bytes):
            if len(new_byte) != 1:
                raise ValueError("byte must be a single byte!")
        self._byte = new_byte

    @property
    def compressed_data(self):
        return_string = self.cmd_and_reps_bytes
        return_string += self._byte

        return return_string


class TektonWordFillField(TektonField):
    command_code = 0b010

    def __init__(self):
        super(TektonWordFillField, self).__init__()
        self._word = b'\x00\x00'

    @property
    def word(self):
        """bytes: Returns the word (two bytes) which this field is filled with."""
        return self._word

    @word.setter
    def word(self, new_word):
        if not isinstance(new_word, (int, bytes)):
            raise TypeError("word must be of type int or bytes. You may use hex notation, e.g. 0x39f2")
        if isinstance(new_word, bytes):
            if len(new_word) != 2:
                raise ValueError("word must contain exactly two bytes!")
        if isinstance(new_word, int):
            if new_word < 0 or new_word > 65535:
                raise ValueError("word must be between 0 and 65535 (0x0000 and 0xffff)")
            new_word = new_word.to_bytes(2, byteorder="big")
        self._word = new_word

    @property
    def compressed_data(self):
        return_string = self.cmd_and_reps_bytes
        return_string += self._word

        return return_string



class TektonL1RepeaterField:
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
        self.h_mirror = False
        self.v_mirror = False

        self._tileno = 0x00

    def __repr__(self):
        """Returns a textual representation of the L1RepeaterField.

        Returns:
            str : A textual representation of the L1RepeaterField's attributes.

        """

        template_string = "Layer 1 Repeater Field:\n Repetitions: {num_reps}\n BTS Type: {bts_type}\n Tile Number: {tileno}, \n H Mirror: {h_mirror}\n V Mirror: {v_mirror}"
        return template_string.format(num_reps=self.num_reps,
                                      bts_type=self.bts_type,
                                      tileno=self.tileno,
                                      h_mirror=self.h_mirror,
                                      v_mirror=self.v_mirror)

    def __eq__(self, other):
        """Determines whether two L1RepeaterFields specify identical tiles attributes and number of repetitions.

        L1RepeaterFields are designed to be fungible. Two L1RepeaterFields are equivalent if they specify identical
        tile attributes and if they have the same number of repetitions.

        Args:
            other (TektonL1RepeaterField): Another L1RepeaterField object for comparing to this one.

        Returns:
            bool : True if both L1RepeaterFields have identical tile attributes and number of repetitions. Otherwise
                False.

        """

        if not isinstance(other, TektonL1RepeaterField):
            raise TypeError("Must compare two L1RepeaterField objects!")
        return self.num_reps == other.num_reps and \
               self._tileno == other._tileno and \
               self.bts_type == other.bts_type and \
               self.h_mirror == other.h_mirror and \
               self.v_mirror == other.v_mirror

    def __ne__(self, other):
        """Returns True if two L1RepeaterFields do NOT specify identical attributes and repetitions, otherwise False.

        L1RepeaterFields are designed to be fungible. Two L1RepeaterFields are equivalent if they specify identical
        tile attributes and if they have the same number of repetitions.

        Args:
            other (TektonL1RepeaterField): Another L1RepeaterField object for comparing to this one.

        Returns:
            bool : False if both L1RepeaterFields have identical tile attributes and number of repetitions. Otherwise
                True.

        """

        if not isinstance(other, TektonL1RepeaterField):
            raise TypeError("Must compare two L1RepeaterField objects!")
        return not (self == other)

    @property
    def tileno(self):
        """int: The tile number in the tileset used by this tile. Values must be between 0 and 0x3ff (1023)"""
        return self._tileno

    @tileno.setter
    def tileno(self, new_tileno):
        if not (isinstance(new_tileno, int)):
            raise TypeError("tileno must be int! You can use hex notation if you like, e.g. 0x10a")
        if new_tileno < 0 or new_tileno > 0x3ff:
            raise ValueError("tileno must be between 0 and 0x3ff (1023)")
        self._tileno = new_tileno

    @property
    def field_header_and_reps_bytes(self):
        field_header = int.from_bytes(b'\xe8\x01', byteorder="big")
        field_header += ((self.num_reps - 1) << 1)
        return field_header.to_bytes(2, byteorder="big")

    @property
    def attributes_bytes(self):
        """bytes: Two bytes representing the tile number, tile mirror, and bts data of this tile."""
        bytes_value = self._tileno
        if self.h_mirror:
            bytes_value += 0b0000010000000000
        if self.v_mirror:
            bytes_value += 0b0000100000000000
        bytes_value += (self.bts_type << 12)
        return bytes_value.to_bytes(2, byteorder="little")

    @property
    def compressed_data(self):
        """str: The string of bytes representing the repeated tiles in the compressed level data."""
        return_string = self.field_header_and_reps_bytes
        return_string += self.attributes_bytes
        return return_string


class TektonBTSNumRepeaterField:
    """An object representing the bts number of a single tile repeated a specific number of times in the level data.

    Super Metroid employs a number of "shorthand" statements to compress level data. One of the shorthands is to
    specify a bts number and the number of times that tile is to be repeated (horizontally from left to right, wrapping
    around to the next row of tiles if necessary.) This shorthand requires only a few bytes to represent many tiles' BTS
    number. This object contains the bts number and number of times it is repeated, and can output the compressed bytes
    that can be concatenated into a larger set of level data.

    BTSNumRepeaterFields are considered fungible, and are compared by value rather than by reference. Two
    BTSNumRepeaterFields are equivalent if they specify identical bts numbers and have the same number of repetitions.

    Attributes:
        num_reps (int): The number of times the specific tile is repeated. Super Metroid will "wrap" these tiles onto
            the next row if they exceed beyond the width of the room.
        bts_num (int): BTS number to be repeated.

    """

    def __init__(self):
        self.num_reps = 0
        self.bts_num = 0

    def __repr__(self):
        """Returns a textual representation of the BTSNumRepeaterField.

        Returns:
            str : A textual representation of the BTSNumRepeaterField's attributes.

        """

        template_string = "BTS Number Repeater Field:\n Repetitions: {num_reps}\n BTS Number: {bts_num}"
        return template_string.format(num_reps=self.num_reps,
                                      bts_num=self.bts_num)

    def __eq__(self, other):
        """Determines whether two BTSNumRepeaterFields specify identical tiles attributes and number of repetitions.

        BTSNumRepeaterFields are designed to be fungible. Two BTSNumRepeaterFields are equivalent if they specify
        identical bts numbers and the same number of repetitions.

        Args:
            other (TektonBTSNumRepeaterField): Another BTSNumRepeaterField object for comparing to this one.

        Returns:
            bool : True if both BTSNumRepeaterFields have identical tile attributes and number of repetitions. Otherwise
                False.

        """

        if not isinstance(other, TektonBTSNumRepeaterField):
            raise TypeError("Must compare two BTSNumRepeaterField objects!")
        return self.num_reps == other.num_reps and \
               self.bts_num == other.bts_num

    def __ne__(self, other):
        """Returns True if two BTSNumRepeaterFields specify identical bts nubmers and number of repetitions, else False.

        BTSNumRepeaterFields are designed to be fungible. Two BTSNumRepeaterFields are equivalent if they specify
        identical bts numbers and the same number of repetitions.

        Args:
            other (TektonBTSNumRepeaterField): Another BTSNumRepeaterField object for comparing to this one.

        Returns:
            bool : False if both BTSNumRepeaterFields have identical bts numbers and number of repetitions. Otherwise
                True.

        """

        if not isinstance(other, TektonBTSNumRepeaterField):
            raise TypeError("Must compare two BTSNumRepeaterField objects!")
        return not (self == other)

    @property
    def field_header_and_reps_bytes(self):
        field_header = int.from_bytes(b'\xe4\x00', byteorder="big")
        field_header += (self.num_reps - 1)
        return field_header.to_bytes(2, byteorder="big")

    @property
    def bts_number_byte(self):
        """bytes: One byte representing the bts number of this tile."""
        return self.bts_num.to_bytes(1, byteorder="big")

    @property
    def compressed_data(self):
        """str: The string of bytes representing the repeated bts number in the compressed level data."""
        return_string = self.field_header_and_reps_bytes
        return_string += self.bts_number_byte
        return return_string


class TektonBTSNumSingleField:
    """An object representing the BTS number of a single tile in compressed level data.

    Super Metroid employs a number of "shorthand" statements in its compressed level data. Often these shorthands
    involve specifying a tile and a number of times to repeat that tile. However, if the room contains just a single
    tile of any type, it is not possible to use a shorthand statement to represent it. This object contains the bts
    number of a single tile, and can output the compressed bytes that can be concatenated into a larger set of level
    data.

    BTSNumRepeaterFields are considered fungible, and are compared by value rather than by reference. Two
    BTSNumRepeaterFields are equivalent if they specify identical bts numbers and have the same number of repetitions.

    Attributes:
        bts_num (int): BTS number of the single block.

    """

    def __init__(self):
        self.bts_num = 0x00

    def __repr__(self):
        """Returns a textual representation of the BTSNumSingleField.

        Returns:
            str : A textual representation of the BTSNumSingleField's attributes.

        """

        template_string = "BTS Number Single Field:\n BTS Number: {bts_num}"
        return template_string.format(bts_num=self.bts_num)

    def __eq__(self, other):
        """Determines whether two BTSNumSingleFields specify identical BTS numbers.

        BTSNumSingleFields are designed to be fungible. Two BTSNumSingleFields are equivalent if they specify
        identical bts numbers.

        Args:
            other (TektonBTSNumSingleField): Another BTSNumSingleField object for comparing to this one.

        Returns:
            bool : True if both BTSNumSingleFields have identical tile attributes and number of repetitions. Otherwise
                False.

        """

        if not isinstance(other, TektonBTSNumSingleField):
            raise TypeError("Must compare two BTSNumSingleField objects!")
        return self.bts_num == other.bts_num

    @property
    def field_header_byte(self):
        """bytes: One byte representing the field header for this Field."""
        return b'\x00'

    @property
    def bts_number_byte(self):
        """bytes: One byte representing the bts number of this tile."""
        return self.bts_num.to_bytes(1, byteorder="big")

    @property
    def compressed_data(self):
        """str: The string of bytes representing the single bts number in the compressed level data."""
        return_string = self.field_header_byte
        return_string += self.bts_number_byte
        return return_string