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
    if "level_data_length" in test_room_data.keys():
        test_room.level_data_length = test_room_data["level_data_length"]
    if "standard_state" in test_room_data.keys():
        test_room.standard_state = load_room_state_from_test_data(test_room_data["standard_state"], test_room_data["room_width"], test_room_data["room_height"])
    if "extra_states" in test_room_data.keys():
        for extra_state in test_room_data["extra_states"]:
            test_room.extra_states.append(load_room_state_pointer_from_test_data(extra_state, test_room_data["room_width"], test_room_data["room_height"]))

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
    if test_state_pointer_data["type"] == "flyway_state":
        new_state_pointer = tekton.tekton_room_state.TektonRoomFlywayStatePointer()
        if "event_value" in test_state_pointer_data.keys():
            new_state_pointer.event_value = test_state_pointer_data["event_value"]
        if "room_state" in test_state_pointer_data.keys():
            new_state_pointer.room_state = load_room_state_from_test_data(test_state_pointer_data["room_state"],
                                                                          room_width,
                                                                          room_height)
    if test_state_pointer_data["type"] == "landing_state":
        new_state_pointer = tekton.tekton_room_state.TektonRoomEventStatePointer()
        if "room_state" in test_state_pointer_data.keys():
            new_state_pointer.room_state = load_room_state_from_test_data(test_state_pointer_data["room_state"],
                                                                          room_width,
                                                                          room_height)
    return new_state_pointer

def load_room_state_from_test_data(test_state_data, room_width, room_height):
    new_state = tekton.tekton_room_state.TektonRoomState()
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