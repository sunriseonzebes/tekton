"""Tekton Tile Grid

This module implements a two-dimensional matrix for storing and organizing TektonTile objects.

Classes:
    TektonTileGrid: A two-dimensional list that organizes TektonTile objects."""

from .tekton_tile import TektonTile

class TektonTileGrid:
    """A two-dimensional list for storing and organizing TektonTile objects.

    TektonTileGrids contain no TektonTile objects when instantiated, see the fill() function.

    Attributes:
        (none)

    """

    def __init__(self, width, height):
        self._tiles = [[None for row in range(height)] for col in range(width)]

    def __getitem__(self, item):
        """Allows you to get a specific column from the grid by index.

        Each column is a list of TektonTile objects, so you can specify column/row by doing grid_object[5][3]

        Args:
            item (int) Index of the column (x-coordinate) you want

        Returns:
            list : List of TektonTiles contained in the specified column, indexed by row.

        """

        return self._tiles[item]

    @property
    def width(self):
        """int: Number of columns contained in the TektonTileGrid."""
        return len(self._tiles)

    @property
    def height(self):
        """int: Number of rows contained in the TektonTileGrid."""
        return len(self._tiles[0])

    @property
    def uncompressed_data(self):
        """bytes: String of uncompressed data, matching what the level data looks like in game RAM."""
        return_string = b''
        for y in range(self.height):
            for x in range(self.width):
                return_string += self._tiles[x][y].l1_attributes_bytes
        for y in range(self.height):
            for x in range(self.width):
                return_string += self._tiles[x][y].bts_number_byte

        return return_string


    def fill(self):
        """Fills every column/row in the TektonTileGrid with a default TektonTile object."""
        for row in range(self.height):
            for col in range(self.width):
                self._tiles[col][row] = TektonTile()
