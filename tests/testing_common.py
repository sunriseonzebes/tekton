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

def load_room_from_test_tiles(test_tile_data):
    test_room = tekton.tekton_room.TektonRoom(test_tile_data["room_width"], test_tile_data["room_height"])
    tiles_width = test_room.tiles.width
    if "level_data_length" in test_tile_data.keys():
        test_room.level_data_length = test_tile_data["level_data_length"]
    counter = 0
    for tile_group in test_tile_data["test_tiles"]:
        for i in range(tile_group["count"]):
            for key in tile_group["tile"].keys():
                setattr(test_room.tiles[counter % tiles_width][counter // tiles_width],
                        key,
                        tile_group["tile"][key])
            counter += 1

    return test_room