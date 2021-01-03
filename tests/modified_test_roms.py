from testing_common import tekton
from tekton import tekton_project, tekton_system
import json
import os

deltas_list = {
    "blank_room_79d5a": [
        {
            "address": 0x21bcd2,
            "bytes": b'\x01\x00\x02\xe9\xff\x00\x01\xe4\xff\x00',
            "pad": 155
        }
    ]
}


def get_modified_rom_contents(delta_name):
    original_rom_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures', 'original_rom.sfc')
    test_project = tekton_project.TektonProject()
    test_project.source_rom_path = original_rom_path
    modified_rom_contents = test_project.get_source_rom_contents()

    deltas = deltas_list[delta_name]

    # Apply deltas one at a time
    for delta in deltas:
        insert_string = delta["bytes"]
        if "pad" in delta.keys():
            while len(insert_string) < delta["pad"]:
                insert_string += b'\xff'
        modified_rom_contents = tekton_system.overwrite_bytes_at_index(modified_rom_contents, insert_string,
                                                                       delta["address"])

    return modified_rom_contents
