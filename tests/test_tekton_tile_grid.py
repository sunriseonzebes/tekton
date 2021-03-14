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
        test_tile = tekton_tile.TektonTile()
        test_grid._tiles[0][0] = test_tile
        self.assertEqual(test_tile, test_grid[0][0], "TektonTileGrid _get_item did not find correct object!")

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

        unique_tile = tekton_tile.TektonTile()
        unique_tile.tileno = 0x2e0
        unique_tile.bts_type = 0x08

        test_grid = tekton_tile_grid.TektonTileGrid(width, height)
        test_grid.fill(unique_tile)
        for col in range(width):
            for row in range(height):
                self.assertTrue(isinstance(test_grid._tiles[col][row], tekton_tile.TektonTile))
                self.assertEqual(unique_tile, test_grid[col][row], "TektonTileGrid was not filled with correct tile!")

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


    def test_overwrite_with(self):
        bg_grid = tekton_tile_grid.TektonTileGrid(16, 16)
        bg_tile = tekton_tile.TektonTile()
        bg_tile.tileno = 0x080
        bg_tile.bts_type = 0x00
        bg_grid.fill(bg_tile)

        paste_grid = tekton_tile_grid.TektonTileGrid(4, 4)
        paste_tile = tekton_tile.TektonTile()
        paste_tile.tileno = 0x2e0
        paste_tile.bts_type = 0x08
        paste_grid.fill(paste_tile)

        bg_grid.overwrite_with(paste_grid, 10, 6)

        for row in range(6):
            for col in range(16):
                self.assertEqual(bg_tile, bg_grid[col][row], "TileGrid returned incorrect tile!")
        for row in range(6, 10):
            for col in range(16):
                if col >= 10 and col <= 13:
                    self.assertEqual(paste_tile, bg_grid[col][row], "TileGrid returned incorrect tile!")
                else:
                    self.assertEqual(bg_tile, bg_grid[col][row], "TileGrid returned incorrect tile!")
        for row in range(11, 16):
            for col in range(16):
                self.assertEqual(bg_tile, bg_grid[col][row], "TileGrid returned incorrect tile!")

        bg_grid = tekton_tile_grid.TektonTileGrid(16, 16)
        bg_grid.fill(bg_tile)
        paste_grid = tekton_tile_grid.TektonTileGrid(4, 4)
        paste_grid.fill(paste_tile)
        bg_grid.overwrite_with(paste_grid, 15, 14)

        for row in range(14):
            for col in range(16):
                self.assertEqual(bg_tile, bg_grid[col][row], "TileGrid returned incorrect tile!")
        for row in range(14, 16):
            for col in range(16):
                if col == 15:
                    self.assertEqual(paste_tile, bg_grid[col][row], "TileGrid returned incorrect tile!")
                else:
                    self.assertEqual(bg_tile, bg_grid[col][row], "TileGrid returned incorrect tile!")

        bg_grid = tekton_tile_grid.TektonTileGrid(16, 16)
        bg_grid.fill(bg_tile)
        paste_grid = tekton_tile_grid.TektonTileGrid(4, 4)
        paste_grid[2][2] = paste_tile
        bg_grid.overwrite_with(paste_grid, 6, 12)

        for row in range(16):
            for col in range(16):
                if col == 8 and row == 14:
                    self.assertEqual(paste_tile, bg_grid[col][row], "TileGrid returned incorrect tile!")
                else:
                    self.assertEqual(bg_tile, bg_grid[col][row], "TileGrid returned incorrect tile!")