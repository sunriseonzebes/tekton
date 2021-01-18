"""Tekton Tile

This module implements the TektonTile class, which represents a single tile in a Super Metroid room. It has many user-
configurable properties like BTS, mirroring, and more.

Classes:
    TektonTile: Represents a single tile of a Super Metroid room, and properties associated with that tile.

"""

class TektonTile:
    """An object representing a single tile in a Super Metroid room.

    TektonTiles are considered fungible. If the values of two TektonTiles are the same, then those two TektonTiles are
    considered equivalent. When copying a TektonTile (such as when you are filling a room with the same time) you should
    use the copy() function to create unique TektonTile objects for each tile you need.

    Attributes:
        bts_type (int): The BTS number of the tile.
        tileno (int): The number of the tile in the tileset graphics (i.e., what the tile looks like)
        h_mirror (bool): Whether the tile art should be mirrored horizontally
        v_mirror (bool): Whether the tile art should be mirrored vertically.

    """

    def __init__(self):
        self.bts_type = 0x00
        self.tileno = 0x00
        self.h_mirror = False
        self.v_mirror = False

    def __repr__(self):
        """Returns a textual representation of the TektonTile and its properties.

        Returns:
            str : A string describing the tile and its properties.

        """

        template_string = "TektonTile:\n" \
                          "Tile Number: {tileno}\n" \
                          "BTS: {bts}\n" \
                          "Tile Horizontal Mirror: {h_mirror}\n" \
                          "Tile Vertical Mirror: {v_mirror}"
        return template_string.format(tileno=self.tileno,
                                      bts=self.bts_type,
                                      h_mirror=self.h_mirror,
                                      v_mirror=self.v_mirror)

    def __eq__(self, other):
        """Returns True if the values of two TektonTiles are equivalent, otherwise False.

        Args:
            other (TektonTile): Another TektonTile to compare to this one.

        Returns:
              bool : True if all the values of the two TektonTiles are equivalent, otherwise False.

        """

        if not isinstance(other, TektonTile):
            return False
        return self.tileno == other.tileno and \
               self.bts_type == other.bts_type and \
               self.h_mirror == other.h_mirror and \
               self.v_mirror == other.v_mirror

    def __ne__(self, other):
        """Returns False if the values of two TektonTiles are equivalent, otherwise True.

        Args:
            other (TektonTile): Another TektonTile to compare to this one.

        Returns:
            bool : False if the values of two TektonTiles are equivalent, otherwise True.

        """

        return not (self == other)

    def copy(self):
        """Returns a new TektonTile instance with the same attribute values as the original TektonTile.

        Copy should be used whenever you are duplicating TektonTiles, such as when you need to fill a room with copies
        of the same tile.

        Returns:
            TektonTile : A new instance containing the same attribute values as the original TektonTile.

        """
        copied = TektonTile()
        copied.tileno = self.tileno
        copied.bts_type = self.bts_type
        copied.h_mirror = self.h_mirror
        copied.v_mirror = self.v_mirror
        return copied
