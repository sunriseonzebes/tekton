"""Tekton Project

This module implements TektonProject, a top-level object which contains abstractions for all the data in the Super
Metroid ROM. A TektonProject contains all the rooms, header data, and tilesets in the ROM, and can output a modified
ROM based on the values of that data.

Classes:
    TektonProject: A top-level object that contains attributes for rooms, tilesets, and other concepts in Super Metroid.

"""

import os
import yaml

from .tekton_room_importer import import_room_from_rom
from .tekton_room_dict import TektonRoomDict
from .tekton_system import overwrite_bytes_at_index

class TektonProject:
    """A top-level object containing abstractions for concepts Super Metroid, like rooms and tilesets. Can output
    modified ROMs based on changes made to its sub-objects.

    Attributes:
        source_rom_path (str): Path to the original ROM used as the base for this TektonProject.
        rooms (TektonRoomDict): Object containing the TektonRooms which will be written to the modified ROM.

    """

    def __init__(self):
        self.source_rom_path = None
        self.rooms = TektonRoomDict()

    def get_source_rom_contents(self):
        """Returns the byte string contained in the self.source_rom_path file

        Returns:
            bytes : ROM data contained in the self.source_rom_path file

        """

        with open(self.source_rom_path, "rb") as f:
            rom_contents = f.read()
        return rom_contents

    def get_modified_rom_contents(self):
        """Returns the source ROM modified with any changes to the rooms, tilesets, or other parts of the TektonProject.

        Returns:
            bytes : The binary data of the modified ROM. (This can then be written to a file.)

        """
        modified_rom_contents = self.get_source_rom_contents()

        for header_address, room in self.rooms.items():
            if room.write_level_data:
                modified_rom_contents = overwrite_bytes_at_index(modified_rom_contents,
                                                                 room.compressed_level_data(),
                                                                 room.standard_state.level_data_address)
            for door in room.doors:
                modified_rom_contents = overwrite_bytes_at_index(modified_rom_contents,
                                                                 door.door_data,
                                                                 door.data_address)

        return modified_rom_contents

    def import_rooms(self, header_address_file=None):
        """Imports all rooms from the source ROM file. Can optionally accept a path to a json file of header addresses.

        Header address files should be json files. The top element should be a list, sub-elements should be dictionaries
        containing a "header" element and optionally a "name" element. The "header" element should be a string
        specifying the hex address of the room header, prepended by "0x".
        Ex: [ { "header": "0x795d4", "name": "Crateria Tube" }, { "header": "0x7a322", "Red Tower Elevator Room" } ... ]

        If no header file is specified, this function will try to import rooms from all of the standard header addresses
        in a Super Metroid ROM.

        Args:
            header_address_file (str): Optional. The path to a json file containing room header addresses and names.

        """
        default_header_address_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "data",
                                                "default_room_imports.yaml")

        if header_address_file is None:
            header_address_file = default_header_address_file

        with open(header_address_file) as f:
            room_headers = yaml.full_load(f)

        rom_contents = self.get_source_rom_contents()

        for room_data in room_headers:

            new_room = import_room_from_rom(rom_contents, room_data["header"])
            new_room.name = room_data["name"]
            self.rooms.add_room(new_room)




