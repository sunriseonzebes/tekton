from testing_common import tekton
from tekton import tekton_room_state
import unittest


class TestTektonRoomStatePointer(unittest.TestCase):
    def test_init(self):
        test_pointer = tekton_room_state.TektonRoomStatePointer()
        self.assertTrue(isinstance(test_pointer, tekton_room_state.TektonRoomStatePointer),
                        msg="TektonRoomStatePointer did not initialize properly!")


class TestTektonRoomEventStatePointer(unittest.TestCase):
    def test_init(self):
        test_pointer = tekton_room_state.TektonRoomEventStatePointer()
        self.assertTrue(isinstance(test_pointer, tekton_room_state.TektonRoomEventStatePointer),
                        msg="TektonRoomEventStatePointer did not initialize properly!")
        self.assertEqual(0,
                         test_pointer.event_value,
                         "TektonRoomEventStatePointer.event_value did not initialize properly!")
        self.assertIsNone(test_pointer.room_state,
                        msg="TektonRoomEventStatePointer.room_state did not initialize properly!")

    def test_pointer_code(self):
        test_pointer = tekton_room_state.TektonRoomEventStatePointer()
        actual_result = test_pointer.pointer_code
        self.assertEqual(b'\x12\xe6',
                         actual_result,
                         "TektonRoomEventStatePointer returned the wrong pointer code!")


class TestTektonRoomSpecialStatePointer(unittest.TestCase):
    def test_init(self):
        test_pointer = tekton_room_state.TektonRoomSpecialStatePointer()
        self.assertTrue(isinstance(test_pointer, tekton_room_state.TektonRoomSpecialStatePointer),
                        msg="TektonRoomSpecialStatePointer did not initialize properly!")
        self.assertIsNone(test_pointer.room_state,
                        msg="TektonRoomSpecialStatePointer.room_state did not initialize properly!")

    def test_pointer_code(self):
        test_pointer = tekton_room_state.TektonRoomSpecialStatePointer()
        actual_result = test_pointer.pointer_code
        self.assertEqual(b'\x69\xe6',
                         actual_result,
                         "TektonRoomSpecialStatePointer returned the wrong pointer code!")


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
        self.assertIsNone(test_state.tiles,
                         "TektonRoomState.tiles did not initialize correctly!")
        self.assertEqual(0,
                         test_state._level_data_address,
                         "TektonRoomState._level_data_address did not initialize correctly!")

    def test_level_data_address(self):
        test_state = tekton_room_state.TektonRoomState()

        test_state.level_data_address = 0x21bcd2
        self.assertEqual(0x21bcd2, test_state.level_data_address, "Tekton Room does not have correct level data address")

        with self.assertRaises(TypeError):
            test_state.level_data_address = "21bcd2"
        with self.assertRaises(ValueError):
            test_state.level_data_address = -5