from testing_common import tekton, original_rom_path, load_test_data_dir, int_list_to_bytes
from tekton import tekton_room_importer, tekton_room, tekton_door, tekton_room_state, tekton_tile_grid
from pydoc import locate
import os
import unittest


class TestTektonRoomImporter(unittest.TestCase):
    def test_init(self):
        test_importer = tekton_room_importer.TektonRoomImporter()
        self.assertTrue(isinstance(test_importer, tekton_room_importer.TektonRoomImporter),
                        msg="TektonRoomImporter failed to initialize correctly!")
        self.assertEqual(0,
                         test_importer.room_header_address,
                         "TektonRoomImporter.room_header_address did not initialize correctly!")
        self.assertEqual(b'',
                         test_importer.rom_contents,
                         "TektonRoomImporter.rom_contents did not initialize correctly!")
        self.assertEqual(1,
                         test_importer.room_width_screens,
                         "TektonRoomImporter.room_width_screens did not initialize correctly!")
        self.assertEqual(1,
                         test_importer.room_height_screens,
                         "TektonRoomImporter.room_height_screens did not initialize correctly!")
        self.assertEqual({},
                         test_importer.level_data_addresses,
                         "TektonRoomImporter.level_data_addresses did not initialize correctly!")

    def test_import_room_from_rom(self):
        with open(original_rom_path, "rb") as f:
            rom_contents = f.read()
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_room_importer',
                                     'test_import_room_from_rom'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_importer = tekton_room_importer.TektonRoomImporter()
            test_importer.rom_contents = rom_contents
            test_importer.room_header_address = test_item["header"]
            test_room = test_importer.import_room_from_rom()
            self.assertTrue(isinstance(test_room, tekton_room.TektonRoom))
            self.assertEqual(test_item["header"],
                             test_room.header,
                             "Room {} imported incorrect header address!".format(hex(test_item["header"])))
            self.assertEqual(test_item["width"],
                             test_room.width_screens,
                             "Room {} imported incorrect width value!".format(hex(test_item["header"])))
            self.assertEqual(test_item["height"],
                             test_room.height_screens,
                             "Room {} imported incorrect height value!".format(hex(test_item["header"])))
            self.assertEqual(test_item["room_index"],
                             test_room.room_index,
                             "Room {} imported incorrect room index!".format(hex(test_item["header"])))
            self.assertEqual(tekton_room.MapArea(test_item["map_area"]),
                             test_room.map_area,
                             "Room {} imported incorrect map_area!".format(hex(test_item["header"])))
            self.assertEqual(test_item["minimap_x_coord"],
                             test_room.minimap_x_coord,
                             "Room {} imported incorrect minimap_x_coord!".format(hex(test_item["header"])))
            self.assertEqual(test_item["minimap_y_coord"],
                             test_room.minimap_y_coord,
                             "Room {} imported incorrect minimap_y_coord!".format(hex(test_item["header"])))
            self.assertEqual(test_item["up_scroller"],
                             test_room.up_scroller,
                             "Room {} imported incorrect up_scroller!".format(hex(test_item["header"])))
            self.assertEqual(test_item["down_scroller"],
                             test_room.down_scroller,
                             "Room {} imported incorrect down_scroller!".format(hex(test_item["header"])))
            self.assertEqual(test_item["special_graphics_bitflag"],
                             test_room.special_graphics_bitflag,
                             "Room {} imported incorrect special_graphics_bitflag!".format(hex(test_item["header"])))
            self.assertTrue(isinstance(test_room.standard_state, tekton_room_state.TektonRoomState),
                            msg="Room Standard State is not an instance of TektonRoomState!")
            self._test_room_state(test_room.standard_state, test_item["standard_state"], test_item["header"], test_item["width"], test_item["height"])
            self.assertEqual(len(test_item["extra_states"]),
                             len(test_room.extra_states),
                             "Room {} has incorrect number of extra state pointers!".format(hex(test_item["header"])))
            for i in range(len(test_item["extra_states"])):
                self._test_room_state_pointer(test_room.extra_states[i], test_item["extra_states"][i], test_item["header"], test_item["width"], test_item["height"])

            level_data_addresses = {test_item["standard_state"]["level_data_address"]: test_room.standard_state.tiles}

            for i in range(len(test_item["extra_states"])):
                extra_level_data_address = test_item["extra_states"][i]["state"]["level_data_address"]
                if extra_level_data_address in level_data_addresses.keys():
                    self.assertEqual(id(level_data_addresses[extra_level_data_address]),
                                     id(test_room.extra_states[i].room_state.tiles),
                                     "Room {} has identical level data addresses that do not have the same TektonTileGrid!".format(hex(test_item["header"])))
                else:
                    level_data_addresses[extra_level_data_address] = test_room.extra_states[i].room_state.tiles


            # TODO: Make this assertEqual once I figure out how to tell where door data ends
            self.assertLessEqual(len(test_item["doors"]),
                             len(test_room.doors),
                             "Test room {0} expected to import {1} doors, but imported {2}!\n{3}".format(
                    hex(test_item["header"]),
                    len(test_item["doors"]),
                    len(test_room.doors),
                    [hex(door.data_address) for door in test_room.doors]
                ))
            for i in range(len(test_item["doors"])):
                expected_door_address = test_item['doors'][i]
                actual_door = test_room.doors[i]
                self.assertEqual(expected_door_address,
                                 actual_door.data_address,
                                 "Door {} imported incorrect data address!".format(i))

        test_importer = tekton_room_importer.TektonRoomImporter()
        test_importer.rom_contents = rom_contents
        test_importer.room_header_address = 0x795d3
        with self.assertRaises(ValueError):
            test_room = test_importer.import_room_from_rom()
        test_importer.room_header_address = "795d4"
        with self.assertRaises(TypeError):
            test_room = test_importer.import_room_from_rom()

    def test_get_door_data_addresses(self):
        with open(original_rom_path, "rb") as f:
            rom_contents = f.read()
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_room_importer',
                                     'test_get_door_data_addresses'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_importer = tekton_room_importer.TektonRoomImporter()
            test_importer.rom_contents = rom_contents
            test_importer.room_header_address = test_item["room_header_address"]
            actual_result = test_importer._get_door_data_addresses()

            actual_result = actual_result[0:test_item["num_doors"]]
            self.assertEqual(test_item["door_addresses"],
                             actual_result,
                             "Incorrect door list returned for room {}".format(test_item["room_header_address"]))

    def test_import_door(self):  # TODO: Split this into three tests: import door, _import_simple_door, _import_elevator_launchpad
        with open(original_rom_path, "rb") as f:
            rom_contents = f.read()
        test_data_dir = os.path.join(os.path.dirname((os.path.abspath(__file__))),
                                     'fixtures',
                                     'unit',
                                     'test_tekton_room_importer',
                                     'test_import_door'
                                     )
        test_data = load_test_data_dir(test_data_dir)

        for test_item in test_data:
            test_importer = tekton_room_importer.TektonRoomImporter()
            test_importer.rom_contents = rom_contents
            test_door = test_importer.import_door(test_item["door_address"])
            expected_results = test_item["expected_results"]
            self.assertTrue(isinstance(test_door, locate(expected_results["type"])),
                            msg="Door at address {0} is type {1}, expected {2}".format(
                                hex(test_item["door_address"]),
                                type(test_door),
                                expected_results["type"]
                            ))
            self.assertEqual(test_item["door_address"], test_door.data_address, "Door has incorrect data address!")
            if isinstance(test_door, tekton_door.TektonDoor):
                expected_results["bit_flag"] = tekton_door.DoorBitFlag[expected_results["bit_flag"]]
                expected_results["direction"] = tekton_door.DoorEjectDirection[expected_results["direction"]]
                self.assertEqual(expected_results["room_id"], test_door.target_room_id, "Door has wrong target room id!")
                self.assertEqual(expected_results["bit_flag"], test_door.bit_flag, "Door has wrong bit flag!")
                self.assertEqual(expected_results["direction"], test_door.eject_direction, "Door has wrong eject direction!")
                self.assertEqual(expected_results["door_cap_x"],
                                 test_door.target_door_cap_col,
                                 "Door has wrong exit door cap x coordinate!")
                self.assertEqual(expected_results["door_cap_y"],
                                 test_door.target_door_cap_row,
                                 "Door has wrong exit door cap y coordinate!")
                self.assertEqual(expected_results["screen_x"],
                                 test_door.target_room_screen_h,
                                 "Door has wrong target room horizontal screen!")
                self.assertEqual(expected_results["screen_y"],
                                 test_door.target_room_screen_v,
                                 "Door has wrong target room vertical screen!")
                self.assertEqual(expected_results["distance_to_spawn"],
                                 test_door.distance_to_spawn,
                                 "Door has wrong distance to spawn!")
                self.assertEqual(expected_results["asm_pointer"], test_door.asm_pointer, "Door has wrong ASM pointer!")
            if isinstance(test_door, tekton_door.TektonElevatorLaunchpad):
                self.assertEqual(int_list_to_bytes(expected_results["door_data"]),
                                 test_door.door_data,
                                 "Elevator Launchpad has incorrect door data!")

            test_importer = tekton_room_importer.TektonRoomImporter()
            test_importer.rom_contents = rom_contents
            with self.assertRaises(TypeError):
                test_door = test_importer.import_door("0x18ac6")
            with self.assertRaises(ValueError):
                test_door = test_importer.import_door(-5)

    def _test_room_state_pointer(self, actual_result, expected_result, room_header_address, room_width, room_height):
        print(actual_result)
        if expected_result["type"] == "event_state":
            self.assertTrue(isinstance(actual_result, tekton_room_state.TektonRoomEventStatePointer),
                            msg="Room state is not correct type!")
        if expected_result["type"] == "landing_state":
            self.assertTrue(isinstance(actual_result, tekton_room_state.TektonRoomLandingStatePointer),
                            msg="Room state is not correct type!")
        if expected_result["type"] == "flyway_state":
            self.assertTrue(isinstance(actual_result, tekton_room_state.TektonRoomFlywayStatePointer),
                            msg="Room state is not correct type!")
        if "event_value" in expected_result:
            self.assertEqual(expected_result["event_value"],
                             actual_result.event_value,
                             "Room {} Room State Pointer has incorrect event value!".format(hex(room_header_address)))
        self._test_room_state(actual_result.room_state, expected_result["state"], room_header_address, room_width, room_height)

    def _test_room_state(self, actual_result, expected_result, room_header_address, room_width, room_height):
        self.assertEqual(expected_result["level_data_address"],
                         actual_result.level_data_address,
                         "Room {} state imported incorrect level data address!".format(
                             hex(room_header_address)))
        self.assertEqual(tekton_room_state.TileSet(expected_result["tileset"]),
                         actual_result.tileset,
                         "Room {} state imported incorrect tileset!".format(hex(room_header_address)))
        self.assertEqual(tekton_room_state.SongSet(expected_result["songset"]),
                         actual_result.songset,
                         "Room {} state imported incorrect songset!".format(hex(room_header_address)))
        self.assertEqual(tekton_room_state.SongPlayIndex(expected_result["song_play_index"]),
                         actual_result.song_play_index,
                         "Room {} state imported incorrect song_play_index!".format(hex(room_header_address)))
        self.assertEqual(expected_result["fx_pointer"],
                         actual_result.fx_pointer,
                         "Room {} state imported incorrect fx_pointer!".format(hex(room_header_address)))
        self.assertEqual(expected_result["enemy_set_pointer"],
                         actual_result.enemy_set_pointer,
                         "Room {} state imported incorrect enemy_set_pointer!".format(
                             hex(room_header_address)))
        self.assertEqual(expected_result["enemy_gfx_pointer"],
                         actual_result.enemy_gfx_pointer,
                         "Room {} state imported incorrect enemy_gfx_pointer!".format(
                             hex(room_header_address)))
        self.assertEqual(expected_result["background_x_scroll"],
                         actual_result.background_x_scroll,
                         "Room {} state imported incorrect background_x_scroll!".format(
                             hex(room_header_address)))
        self.assertEqual(expected_result["background_y_scroll"],
                         actual_result.background_y_scroll,
                         "Room {} state imported incorrect background_y_scroll!".format(
                             hex(room_header_address)))
        self.assertEqual(expected_result["room_scrolls_pointer"],
                         actual_result.room_scrolls_pointer,
                         "Room {} state imported incorrect room_scrolls_pointer!".format(
                             hex(room_header_address)))
        self.assertEqual(expected_result["unused_pointer"],
                         actual_result.unused_pointer,
                         "Room {} state imported incorrect unused_pointer!".format(
                             hex(room_header_address)))
        self.assertEqual(expected_result["main_asm_pointer"],
                         actual_result.main_asm_pointer,
                         "Room {} state imported incorrect main_asm_pointer!".format(
                             hex(room_header_address)))
        self.assertEqual(expected_result["plm_set_pointer"],
                         actual_result.plm_set_pointer,
                         "Room {} state imported incorrect plm_set_pointer!".format(
                             hex(room_header_address)))
        self.assertEqual(expected_result["background_pointer"],
                         actual_result.background_pointer,
                         "Room {} state imported incorrect background_pointer!".format(
                             hex(room_header_address)))
        self.assertEqual(expected_result["setup_asm_pointer"],
                         actual_result.setup_asm_pointer,
                         "Room {} state imported incorrect setup_asm_pointer!".format(
                             hex(room_header_address)))
        self.assertTrue(isinstance(actual_result.tiles, tekton_tile_grid.TektonTileGrid),
                        msg="Room {} state tiles did not initialize correctly!".format(hex(room_header_address)))
        self.assertEqual(room_width * 16,
                         actual_result.tiles.width,
                         "Room {} imported incorrect tile grid width value!".format(hex(room_header_address)))
        self.assertEqual(room_height * 16,
                         actual_result.tiles.height,
                         "Room {} imported incorrect tile grid height value!".format(hex(room_header_address)))