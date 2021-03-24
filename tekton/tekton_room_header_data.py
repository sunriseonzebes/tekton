"""Tekton Room Header Data

This module implements classes that store data found in room headers in the source ROM. Room headers contain a wide
variety of data about a room, including its minimap coordinates, map area, and other information.

Classes:
    MapArea: Enum listing the different regions on the planet.
    TektonRoomHeaderData: An object that stores data found in room headers in the ROM.

"""

from enum import Enum


class MapArea(Enum):
    """Enumeration that lists out the different regions of the planet."""
    CRATERIA = 0x00
    BRINSTAR = 0x01
    NORFAIR = 0x02
    WRECKED_SHIP = 0x03
    MARIDIA = 0x04
    TOURIAN = 0x05
    CERES = 0x06
    DEBUG = 0x07


class TektonRoomHeaderData:
    def __init__(self):
        self.room_index = 0
        self.map_area = MapArea.CRATERIA
        self.minimap_x_coord = 0
        self.minimap_y_coord = 0
        self.up_scroller = 0
        self.down_scroller = 0
        self.special_graphics_bitflag = 0