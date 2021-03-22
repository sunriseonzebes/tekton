from testing_common import tekton
from tekton import tekton_room_state
import unittest

class TestTektonRoomState(unittest.TestCase):
    def test_init(self):
        test_state = tekton_room_state.TektonRoomState()
        self.assertTrue(isinstance(test_state, tekton_room_state.TektonRoomState))
        self.assertEqual(tekton_room_state.TileSet.CRATERIA_CAVE,
                         test_state.tileset,
                         "TektonRoomState.tileset did not initialize correctly!")
        self.assertEqual(tekton_room_state.SongSet.INTRO,
                         test_state.songset,
                         "TektonRoomState.songset did not initialize correctly!")
        self.assertEqual(tekton_room_state.SongPlayIndex.NO_CHANGE,
                         test_state.song_play_index,
                         "TektonRoomState.song_play_index did not initialize correctly!")
        self.assertEqual(0,
                         test_state.fx_pointer,
                         "TektonRoomState.fx_pointer did not initialize correctly!")
        self.assertEqual(0,
                         test_state.enemy_set_pointer,
                         "TektonRoomState.enemy_set_pointer did not initialize correctly!")
        self.assertEqual(0,
                         test_state.enemy_gfx_pointer,
                         "TektonRoomState.enemy_gfx_pointer did not initialize correctly!")
        self.assertEqual(0,
                         test_state.enemy_set_pointer,
                         "TektonRoomState.enemy_set_pointer did not initialize correctly!")
        self.assertEqual(0,
                         test_state.background_x_scroll,
                         "TektonRoomState.background_x_scroll did not initialize correctly!")
        self.assertEqual(0,
                         test_state.background_y_scroll,
                         "TektonRoomState.background_y_scroll did not initialize correctly!")
        self.assertEqual(0,
                         test_state.room_scrolls_pointer,
                         "TektonRoomState.room_scrolls_pointer did not initialize correctly!")
        self.assertEqual(0,
                         test_state.unused_pointer,
                         "TektonRoomState.unused_pointer did not initialize correctly!")
        self.assertEqual(0,
                         test_state.main_asm_pointer,
                         "TektonRoomState.main_asm_pointer did not initialize correctly!")
        self.assertEqual(0,
                         test_state.setup_asm_pointer,
                         "TektonRoomState.main_asm_pointer did not initialize correctly!")
        self.assertEqual(0,
                         test_state._level_data_address,
                         "TektonRoomState._level_data_address did not initialize correctly!")
