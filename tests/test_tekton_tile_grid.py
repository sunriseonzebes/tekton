from testing_common import tekton, load_test_data_dir, int_list_to_bytes, load_room_from_test_tiles
from tekton import tekton_tile_grid, tekton_tile
import os
import unittest

class TestTektonTileGrid(unittest.TestCase):
    def test_init(self):
        test_grid = tekton_tile_grid.TektonTileGrid(16, 16)
        self.assertIsNotNone(test_grid)
        self.assertEqual(len(test_grid._tiles), 16, "Tekton Tile Grid does not contain enough columns of tiles")
        for col in range(16):
            self.assertEqual(len(test_grid._tiles[col]), 16, "Tekton Tile Grid does not contain enough rows of tiles")
            for row in range(16):
                self.assertIsNone(test_grid._tiles[col][row])

    def test_width(self):
        test_grid = tekton_tile_grid.TektonTileGrid(16, 32)
        self.assertEqual(test_grid.width, 16)

    def test_height(self):
        test_grid = tekton_tile_grid.TektonTileGrid(32, 16)
        self.assertEqual(test_grid.height, 16)

    def test_get_item(self):
        test_grid = tekton_tile_grid.TektonTileGrid(1, 1)
        self.assertIsNone(test_grid[0][0])

    def test_fill(self):
        width = 16
        height = 16
        test_grid = tekton_tile_grid.TektonTileGrid(width, height)
        for col in range(width):
            for row in range(height):
                self.assertIsNone(test_grid._tiles[col][row])

        test_grid.fill()

        for col in range(width):
            for row in range(height):
                self.assertTrue(isinstance(test_grid._tiles[col][row], tekton_tile.TektonTile))

    def test_uncompressed_data(self):
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_tile_grid',
                                     'test_uncompressed_data'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_case in test_data:
            expected_result = int_list_to_bytes(test_case["expected_result"])
            test_room = load_room_from_test_tiles(test_case)
            actual_result = test_room.tiles.uncompressed_data
            self.assertEqual(expected_result,
                             actual_result,
                             "Test room did not produce correct uncompressed data!")

