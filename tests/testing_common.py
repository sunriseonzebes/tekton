import os
import sys
import yaml
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "", "..")))

import tekton
original_rom_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "fixtures", "original_rom.sfc")


def load_test_data_dir(test_data_dir):
    test_data = []
    for filename in os.listdir(test_data_dir):
        test_data.append(load_test_data_file(os.path.join(test_data_dir, filename)))

    return test_data


def load_test_data_file(test_data_file):
    with open(test_data_file) as f:
        test_file_contents = yaml.full_load(f)

    return test_file_contents


def int_list_to_bytes(int_list):
    bytes_value = b''
    for el in int_list:
        bytes_value += el.to_bytes(1, byteorder="big")
    return bytes_value

def load_room_from_test_data(test_room_data):
    test_room = tekton.tekton_room.TektonRoom(test_room_data["room_width"], test_room_data["room_height"])
    if "header" in test_room_data.keys():
        test_room.header = test_room_data["header"]
    if "down_scroller" in test_room_data.keys():
        test_room.down_scroller = test_room_data["down_scroller"]
    if "level_data_length" in test_room_data.keys():
        test_room.level_data_length = test_room_data["level_data_length"]
    if "map_area" in test_room_data.keys():
        test_room.map_area = tekton.tekton_room.MapArea(test_room_data["map_area"])
    if "minimap_x_coord" in test_room_data.keys():
        test_room.minimap_x_coord = test_room_data["minimap_x_coord"]
    if "minimap_y_coord" in test_room_data.keys():
        test_room.minimap_y_coord = test_room_data["minimap_y_coord"]
    if "name" in test_room_data.keys():
        test_room.name = test_room_data["name"]
    if "room_index" in test_room_data.keys():
        test_room.room_index = test_room_data["room_index"]
    if "special_graphics_bitflag" in test_room_data.keys():
        test_room.special_graphics_bitflag = test_room_data["special_graphics_bitflag"]
    if "up_scroller" in test_room_data.keys():
        test_room.up_scroller = test_room_data["up_scroller"]
    if "standard_state" in test_room_data.keys():
        test_room.standard_state = load_room_state_from_test_data(test_room_data["standard_state"], test_room_data["room_width"], test_room_data["room_height"])
    if "extra_states" in test_room_data.keys():
        for extra_state in test_room_data["extra_states"]:
            test_room.extra_states.append(load_room_state_pointer_from_test_data(extra_state, test_room_data["room_width"], test_room_data["room_height"]))
    if "doors" in test_room_data.keys():
        for door_data in test_room_data["doors"]:
            test_room.doors.append(load_door_from_test_data(door_data))

    return test_room

def load_room_state_pointer_from_test_data(test_state_pointer_data, room_width, room_height):
    new_state_pointer = None
    if test_state_pointer_data["type"] == "event_state":
        new_state_pointer = tekton.tekton_room_state.TektonRoomEventStatePointer()
        if "event_value" in test_state_pointer_data.keys():
            new_state_pointer.event_value = test_state_pointer_data["event_value"]
        if "room_state" in test_state_pointer_data.keys():
            new_state_pointer.room_state = load_room_state_from_test_data(test_state_pointer_data["room_state"],
                                                                          room_width,
                                                                          room_height)
    elif test_state_pointer_data["type"] == "flyway_state":
        new_state_pointer = tekton.tekton_room_state.TektonRoomFlywayStatePointer()
        if "event_value" in test_state_pointer_data.keys():
            new_state_pointer.event_value = test_state_pointer_data["event_value"]
        if "room_state" in test_state_pointer_data.keys():
            new_state_pointer.room_state = load_room_state_from_test_data(test_state_pointer_data["room_state"],
                                                                          room_width,
                                                                          room_height)
    elif test_state_pointer_data["type"] == "landing_state":
        new_state_pointer = tekton.tekton_room_state.TektonRoomLandingStatePointer()
        if "room_state" in test_state_pointer_data.keys():
            new_state_pointer.room_state = load_room_state_from_test_data(test_state_pointer_data["room_state"],
                                                                          room_width,
                                                                          room_height)
    return new_state_pointer

def load_room_state_from_test_data(test_state_data, room_width, room_height):
    new_state = tekton.tekton_room_state.TektonRoomState()
    if "tileset" in test_state_data.keys():
        new_state.tileset = tekton.tekton_room_state.TileSet(test_state_data["tileset"])
    if "songset" in test_state_data.keys():
        new_state.songset = tekton.tekton_room_state.SongSet(test_state_data["songset"])
    if "song_play_index" in test_state_data.keys():
        new_state.song_play_index = tekton.tekton_room_state.SongPlayIndex(test_state_data["song_play_index"])
    if "fx_pointer" in test_state_data.keys():
        new_state.fx_pointer = test_state_data["fx_pointer"]
    if "enemy_set_pointer" in test_state_data.keys():
        new_state.enemy_set_pointer = test_state_data["enemy_set_pointer"]
    if "enemy_gfx_pointer" in test_state_data.keys():
        new_state.enemy_gfx_pointer = test_state_data["enemy_gfx_pointer"]
    if "background_x_scroll" in test_state_data.keys():
        new_state.background_x_scroll = test_state_data["background_x_scroll"]
    if "background_y_scroll" in test_state_data.keys():
        new_state.background_y_scroll = test_state_data["background_y_scroll"]
    if "room_scrolls_pointer" in test_state_data.keys():
        new_state.room_scrolls_pointer = test_state_data["room_scrolls_pointer"]
    if "unused_pointer" in test_state_data.keys():
        new_state.unused_pointer = test_state_data["unused_pointer"]
    if "main_asm_pointer" in test_state_data.keys():
        new_state.main_asm_pointer = test_state_data["main_asm_pointer"]
    if "plm_set_pointer" in test_state_data.keys():
        new_state.plm_set_pointer = test_state_data["plm_set_pointer"]
    if "background_pointer" in test_state_data.keys():
        new_state.background_pointer = test_state_data["background_pointer"]
    if "setup_asm_pointer" in test_state_data.keys():
        new_state.setup_asm_pointer = test_state_data["setup_asm_pointer"]
    if "level_data_address" in test_state_data.keys():
        new_state.level_data_address = test_state_data["level_data_address"]
    new_state.tiles = tekton.tekton_tile_grid.TektonTileGrid(room_width * 16, room_height * 16)
    new_state.tiles.fill()
    tiles_width = new_state.tiles.width
    counter = 0
    if "tiles" in test_state_data.keys():
        for tile_group in test_state_data["tiles"]:
            for i in range(tile_group["count"]):
                for key in tile_group["tile"].keys():
                    setattr(new_state.tiles[counter % tiles_width][counter // tiles_width],
                            key,
                            tile_group["tile"][key])
                counter += 1

    return new_state

def load_door_from_test_data(test_door_data):
    new_door = tekton.tekton_door.TektonDoor()
    if "data_address" in test_door_data.keys():
        new_door.data_address = test_door_data["data_address"]
    if "target_room_id" in test_door_data.keys():
        new_door.target_room_id = test_door_data["target_room_id"]
    if "target_door_cap_col" in test_door_data.keys():
        new_door.target_door_cap_col = test_door_data["target_door_cap_col"]
    if "target_door_cap_row" in test_door_data.keys():
        new_door.target_door_cap_row = test_door_data["target_door_cap_row"]
    if "target_room_screen_h" in test_door_data.keys():
        new_door.target_room_screen_h = test_door_data["target_room_screen_h"]
    if "target_room_screen_v" in test_door_data.keys():
        new_door.target_room_screen_v = test_door_data["target_room_screen_v"]
    if "distance_to_spawn" in test_door_data.keys():
        new_door.distance_to_spawn = test_door_data["distance_to_spawn"]
    if "asm_pointer" in test_door_data.keys():
        new_door.asm_pointer = test_door_data["asm_pointer"]
    if "bit_flag" in test_door_data.keys():
        new_door.bit_flag = tekton.tekton_door.DoorBitFlag(test_door_data["bit_flag"])
    if "eject_direction" in test_door_data.keys():
        new_door.eject_direction = tekton.tekton_door.DoorEjectDirection(test_door_data["eject_direction"])

    return new_door