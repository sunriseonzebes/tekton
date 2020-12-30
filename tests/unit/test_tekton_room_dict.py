from context import tekton
from tekton import tekton_room_dict, tekton_room
import unittest

class TestTektonRoomDict(unittest.TestCase):
    def test_init(self):
        test_dict = tekton_room_dict.TektonRoomDict()
        self.assertIsNotNone(test_dict)
        self.assertEqual(test_dict._rooms, [])

    def test_get_item(self):
        test_dict = tekton_room_dict.TektonRoomDict()
        test_room = tekton_room.TektonRoom()
        test_room.header = 0x795d4
        test_dict._rooms = [test_room]

        self.assertEqual(test_room, test_dict[0x795d4], "Looking up room by header did not return correct room!")

    def test_keys(self):
        test_dict = tekton_room_dict.TektonRoomDict()
        test_room_1 = tekton_room.TektonRoom()
        test_room_1.header = 0x795d4
        test_room_2 = tekton_room.TektonRoom()
        test_room_2.header = 0x791f8
        test_room_3 = tekton_room.TektonRoom()
        test_room_3.header = 0x7968f
        test_dict._rooms = [test_room_1, test_room_2, test_room_3]

        expected_value = [0x791f8, 0x795d4, 0x7968f]
        test_value = test_dict.keys()

        self.assertEqual(expected_value, test_value, "TektonRoomDict did not return correct list of rooms.")

    def test_items(self):
        test_dict = tekton_room_dict.TektonRoomDict()
        test_room_1 = tekton_room.TektonRoom()
        test_room_1.header = 0x795d4
        test_room_2 = tekton_room.TektonRoom()
        test_room_2.header = 0x791f8
        test_room_3 = tekton_room.TektonRoom()
        test_room_3.header = 0x7968f
        test_dict.add_room(test_room_1)
        test_dict.add_room(test_room_2)
        test_dict.add_room(test_room_3)

        items_iterator = test_dict.items()

        # Test that these iterate correctly, sorted by header address
        self.assertEqual(next(items_iterator), (0x791f8, test_room_2))
        self.assertEqual(next(items_iterator), (0x795d4, test_room_1))
        self.assertEqual(next(items_iterator), (0x7968f, test_room_3))
        with self.assertRaises(StopIteration):
            next(items_iterator)


    def test_add_room(self):
        test_dict = tekton_room_dict.TektonRoomDict()
        test_room_1 = tekton_room.TektonRoom()
        test_room_1.header = 0x795d4
        test_room_2 = tekton_room.TektonRoom()
        test_room_2.header = 0x795d4
        test_dict.add_room(test_room_1)

        expected_value = [test_room_1]
        self.assertEqual(expected_value, test_dict._rooms)

        with self.assertRaises(tekton_room_dict.DuplicateRoomError):
            test_dict.add_room(test_room_2)
