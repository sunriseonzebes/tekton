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