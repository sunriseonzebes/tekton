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
