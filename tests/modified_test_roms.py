from testing_common import tekton, original_rom_path
from tekton import tekton_system


class ROMDelta:
    def __init__(self, new_address, new_bytes, new_pad=0, new_pad_byte=b'\xff'):
        if not isinstance(new_address, int):
            raise TypeError("Address must be int! You can use hex notation, e.g. 0x795d4")
        if not isinstance(new_bytes, bytes):
            raise TypeError("Bytes must be of type bytes!")
        if not isinstance(new_pad, int):
            raise TypeError("Pad must be of type int!")
        if not isinstance(new_pad_byte, bytes):
            raise TypeError("Pad byte must be of type bytes!")
        if not len(new_pad_byte) == 1:
            raise ValueError("Pad byte must be a single byte!")

        self.address = new_address
        self.bytes = new_bytes
        self.pad = new_pad
        self.pad_byte = new_pad_byte


def get_modified_rom_contents(deltas):
    with open(original_rom_path, "rb") as f:
        modified_rom_contents = f.read()

    # Apply deltas one at a time
    for delta in deltas:
        insert_string = delta.bytes
        while len(insert_string) < delta.pad:
            insert_string += delta.pad_byte
        modified_rom_contents = tekton_system.overwrite_bytes_at_index(modified_rom_contents, insert_string,
                                                                       delta.address)

    return modified_rom_contents
