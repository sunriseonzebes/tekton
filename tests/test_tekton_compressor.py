from testing_common import tekton
from tekton import tekton_compressor
from tekton import tekton_tile
from tekton import tekton_room
import os
import unittest


class TestTektonCompressor(unittest.TestCase):
    def test_find_blocks_for_compression(self):
        test_room = tekton_room.TektonRoom()

        for i in range(14):
            test_room.tiles[i][0].tileno = 10
            test_room.tiles[i][0].bts = 8

        first_block = tekton_compressor.RepeaterShorthandBlock()
        first_block.num_reps = 14
        first_block.tile.tileno = 10
        first_block.tile.bts = 8
        last_block = tekton_compressor.RepeaterShorthandBlock()
        last_block.num_reps = 242
        last_block.tile.tileno = 0
        last_block.tile.bts = 0

        test_result = tekton_compressor._find_blocks_for_compression(test_room.tiles)
        expected_result = [first_block, last_block]

        self.assertEqual(test_result, expected_result, "Compressor did not find the correct blocks.")

    def test_generate_compressed_level_data_header(self):
        expected_result = b'\x01\x00\x02'
        test_result = tekton_compressor._generate_compressed_level_data_header()

        self.assertEqual(expected_result, test_result)

    def test_compress_level_data(self):
        test_room = tekton_room.TektonRoom()
        test_room.level_data_length = 155
        test_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                      'fixtures',
                                      'unit',
                                      'sample_compression_data',
                                      'generic_blank_room.bin'
                                      )
        with open(test_file_path, "rb") as f:
            expected_result = f.read()
        test_result = tekton_compressor.compress_level_data(test_room.tiles)
        self.assertEqual(expected_result, test_result, "Room data did not compress correctly.")

        test_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                      'fixtures',
                                      'unit',
                                      'sample_compression_data',
                                      'generic_blank_room_padded.bin'
                                      )
        with open(test_file_path, "rb") as f:
            expected_result = f.read()
        test_result = tekton_compressor.compress_level_data(test_room.tiles, test_room.level_data_length)
        self.assertEqual(expected_result, test_result, "Room data did not compress correctly.")


class TestRepeaterShorthandBlock(unittest.TestCase):
    def test_init(self):
        test_block = tekton_compressor.RepeaterShorthandBlock()
        self.assertIsNotNone(test_block)
        self.assertEqual(test_block.num_reps, 0)
        self.assertTrue(isinstance(test_block.tile, tekton_tile.TektonTile))

    def test_eq(self):
        test_data = [
            {
                "left":
                    {
                        "tile": {"tileno": 0, "bts": 0, "h_mirror": False, "v_mirror": False},
                        "num_reps": 15
                    },
                "right":
                    {
                        "tile": {"tileno": 0, "bts": 0, "h_mirror": False, "v_mirror": False},
                        "num_reps": 15
                    },
                "expected_equal": True
            },
            {
                "left":
                    {
                        "tile": {"tileno": 17, "bts": 0, "h_mirror": False, "v_mirror": False},
                        "num_reps": 24
                    },
                "right":
                    {
                        "tile": {"tileno": 0, "bts": 0, "h_mirror": False, "v_mirror": False},
                        "num_reps": 24
                    },
                "expected_equal": False
            }
        ]

        for test_item in test_data:
            test_block_left = tekton_compressor.RepeaterShorthandBlock()
            test_block_right = tekton_compressor.RepeaterShorthandBlock()

            test_block_left.tile = tekton_tile.TektonTile()
            test_block_left.tile.tileno = test_item["left"]["tile"]["tileno"]
            test_block_left.tile.bts = test_item["left"]["tile"]["bts"]
            test_block_left.tile.h_mirror = test_item["left"]["tile"]["h_mirror"]
            test_block_left.tile.v_mirror = test_item["left"]["tile"]["v_mirror"]
            test_block_left.num_reps = test_item["left"]["num_reps"]

            test_block_right.tile = tekton_tile.TektonTile()
            test_block_right.tile.tileno = test_item["right"]["tile"]["tileno"]
            test_block_right.tile.bts = test_item["right"]["tile"]["bts"]
            test_block_right.tile.h_mirror = test_item["right"]["tile"]["h_mirror"]
            test_block_right.tile.v_mirror = test_item["right"]["tile"]["v_mirror"]
            test_block_right.num_reps = test_item["right"]["num_reps"]

            if test_item["expected_equal"]:
                self.assertEqual(test_block_left, test_block_right)
            else:
                self.assertNotEqual(test_block_left, test_block_right)

    def test_repr(self):
        test_block = tekton_compressor.RepeaterShorthandBlock()
        test_result = test_block.__repr__()
        expected_result = "Repeater Block:\nRepetitions: 0\n Tile: {}".format(test_block.tile)

        self.assertEqual(test_result, expected_result)

    def test_compressed_data(self):
        test_data = [
            {"tileno": 16, "bts": 8, "h_mirror": False, "v_mirror": False, "num_reps": 14,
             "expected_result": b'\xe8\x1b\x10\x81'},
            {"tileno": 10, "bts": 8, "h_mirror": False, "v_mirror": True, "num_reps": 155,
             "expected_result": b'\xe9\x35\x0a\x89'},
            {"tileno": 35, "bts": 7, "h_mirror": True, "v_mirror": False, "num_reps": 209,
             "expected_result": b'\xe9\xa1\x23\x75'},
            {"tileno": 4, "bts": 2, "h_mirror": True, "v_mirror": True, "num_reps": 1,
             "expected_result": b'\xe8\x01\x04\x2d'},
            {"tileno": 21, "bts": 9, "h_mirror": True, "v_mirror": False, "num_reps": 256,
             "expected_result": b'\xe9\xff\x15\x95'},
            {"tileno": 0, "bts": 12, "h_mirror": False, "v_mirror": True, "num_reps": 257,
             "expected_result": b'\xea\x01\x00\xc9'}
        ]

        for test_item in test_data:
            test_block = tekton_compressor.RepeaterShorthandBlock()
            test_block.tile.tileno = test_item["tileno"]
            test_block.tile.bts = test_item["bts"]
            test_block.tile.h_mirror = test_item['h_mirror']
            test_block.tile.v_mirror = test_item['v_mirror']
            test_block.num_reps = test_item["num_reps"]

            test_result = test_block.compressed_data
            expected_result = test_item["expected_result"]

            self.assertEqual(test_result, expected_result, "Error when compressing repeater block {}".format(test_item))
