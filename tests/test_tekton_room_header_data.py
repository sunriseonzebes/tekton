from testing_common import tekton
from tekton import tekton_room_header_data
import unittest

class TestTektonRoomHeaderData(unittest.TestCase):
    def test_init(self):
        test_header_data = tekton_room_header_data.TektonRoomHeaderData()
        self.assertTrue(isinstance(test_header_data, tekton_room_header_data.TektonRoomHeaderData),
                        msg="TektonRoomHeaderData did not initialize correctly!")
        self.assertEqual(0,
                         test_header_data.room_index,
                         "TektonRoomHeaderData room_index did not initialize correctly!")
        self.assertEqual(tekton_room_header_data.MapArea.CRATERIA,
                         test_header_data.map_area,
                         "TektonRoomHeaderData area did not initialize correctly!")
        self.assertEqual(0,
                         test_header_data.minimap_x_coord,
                         "TektonRoomHeaderData minimap_x_coord did not initialize correctly!")
        self.assertEqual(0,
                         test_header_data.minimap_y_coord,
                         "TektonRoomHeaderData minimap_y_coord did not initialize correctly!")
        self.assertEqual(0,
                         test_header_data.up_scroller,
                         "TektonRoomHeaderData up_scroller did not initialize correctly!")
        self.assertEqual(0,
                         test_header_data.down_scroller,
                         "TektonRoomHeaderData down_scroller did not initialize correctly!")
        self.assertEqual(0,
                         test_header_data.special_graphics_bitflag,
                         "TektonRoomHeaderData special_graphics_bitflag did not initialize correctly!")
        self.assertEqual(0,
                         test_header_data.door_out_pointer,
                         "TektonRoomHeaderData door_out_pointer did not initialize correctly!")