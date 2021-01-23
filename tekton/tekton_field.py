"""Tekton Field

Classes:
    L1RepeaterField: An object representing a series of repeating tiles in layer 1 level data

"""


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
            other (L1RepeaterField): Another L1RepeaterField object for comparing to this one.

        Returns:
            bool : True if both L1RepeaterFields have identical tile attributes and number of repetitions. Otherwise
                False.

        """

        if not isinstance(other, L1RepeaterField):
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
            other (L1RepeaterField): Another L1RepeaterField object for comparing to this one.

        Returns:
            bool : False if both L1RepeaterFields have identical tile attributes and number of repetitions. Otherwise
                True.

        """

        if not isinstance(other, L1RepeaterField):
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


class BTSNumRepeaterField:
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
            other (BTSNumRepeaterField): Another BTSNumRepeaterField object for comparing to this one.

        Returns:
            bool : True if both BTSNumRepeaterFields have identical tile attributes and number of repetitions. Otherwise
                False.

        """

        if not isinstance(other, BTSNumRepeaterField):
            raise TypeError("Must compare two BTSNumRepeaterField objects!")
        return self.num_reps == other.num_reps and \
               self.bts_num == other.bts_num

    def __ne__(self, other):
        """Returns True if two BTSNumRepeaterFields specify identical bts nubmers and number of repetitions, else False.

        BTSNumRepeaterFields are designed to be fungible. Two BTSNumRepeaterFields are equivalent if they specify
        identical bts numbers and the same number of repetitions.

        Args:
            other (BTSNumRepeaterField): Another BTSNumRepeaterField object for comparing to this one.

        Returns:
            bool : False if both BTSNumRepeaterFields have identical bts numbers and number of repetitions. Otherwise
                True.

        """

        if not isinstance(other, BTSNumRepeaterField):
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


class BTSNumSingleField:
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
            other (BTSNumSingleField): Another BTSNumSingleField object for comparing to this one.

        Returns:
            bool : True if both BTSNumSingleFields have identical tile attributes and number of repetitions. Otherwise
                False.

        """

        if not isinstance(other, BTSNumSingleField):
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