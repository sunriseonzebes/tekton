"""Tekton Room State

Implements various classes that hold information about a single state for a room. This includes things like what tileset
it uses, what music plays in the room, the scroll speed of the background, etc.

Classes:
    TektonRoomState: An object that holds information about a single state for a room. Rooms can have multiple states so
        each state will get one TektonRoomState.

"""

from enum import Enum

class TileSet(Enum):
    CRATERIA_CAVE = 0x00
    CRATERIA_CAVE_RED = 0x01
    CRATERIA_TECH = 0x02
    CRATERIA_TECH_DARK = 0x03
    WRECKED_SHIP = 0x04
    WRECKED_SHIP_DARK = 0x05
    BRINSTAR_BLUE_GREEN_PINK = 0x06
    BRINSTAR_RED_KRAID = 0x07
    STATUES_HALLWAY = 0x08
    NORFAIR_RED_RIDLEY = 0x09
    NORFAIR_BROWN_CAVE = 0x0a
    MARIDIA_YELLOW = 0x0b
    MARIDIA_PURPLE_SANDTRAP = 0x0c
    TOURIAN = 0x0d
    MOTHER_BRAIN_ROOM = 0x0e
    CERES = 0x0f
    CERES_GREEN = 0x10
    CERES_ENTRANCE = 0x11
    CERES_ENTRANCE_GREEN = 0x12
    CERES_RIDLEY_ROOM = 0x13
    CERES_RIDLEY_ROOM_GREEN = 0x14
    SAVE_ROOM_PINK = 0x15
    SAVE_ROOM_PINK_DARK = 0x16
    SAVE_ROOM_BLUE = 0x17
    SAVE_ROOM_GREEN = 0x18
    SAVE_ROOM_YELLOW = 0x19
    KRAID_ROOM = 0x1a
    CROCOMIRE_ROOM = 0x1b
    DRAYGON_ROOM = 0x1c


class SongSet(Enum):
    INTRO = 0x00
    TITLE_SCREEN = 0x03
    EMPTY_CRATERIA = 0x06
    SPACE_PIRATES = 0x09
    RETURN_TO_CRATERIA = 0x0c
    UPPER_BRINSTAR = 0x0f
    LOWER_BRINSTAR = 0x12
    UPPER_NORFAIR = 0x15
    LOWER_NORFAIR = 0x18
    MARIDIA = 0x1b
    TOURIAN = 0x1e
    MOTHER_BRAIN = 0x21
    BOSS_FIGHT_1 = 0x24
    BOSS_FIGHT_2 = 0x27
    MINIBOSS_FIGHT = 0x2a
    CERES_STATION = 0x2d
    WRECKED_SHIP = 0x30
    ZEBES_EXPLODING = 0x33
    SAMUS_STORY = 0x36
    DEATH_SFX = 0x39
    CREDITS_ROLL = 0x3c
    LAST_METROID_VO = 0x3f
    THE_GALAXY_VO = 0x42
    SUPER_METROID = 0x45
    SAMUS_REVENGE = 0x48


class SongPlayIndex(Enum):
    NO_CHANGE = 0x00
    SAMUS_LOAD = 0x01
    PICKUP_ITEM = 0x02
    ELEVATOR = 0x03
    STATUE_HALL = 0x04
    SONG_1 = 0x05
    SONG_2 = 0x06
    SONG_3 = 0x07
    STOP_MUSIC = 0x80


class TektonRoomStatePointer:
    """A superclass for pointers representing different kinds of room states. Room header data contains zero or more
        pointers to special room states that are not the standard room state.

    Attributes:


    """
    def __init__(self):
        pass

    @property
    def pointer_code(self):
        pass


class TektonRoomEventStatePointer(TektonRoomStatePointer):
    """Class that represents a single event state pointer in room header data. Holds the event state data and the event
        value that triggers the state.

    Attributes:
        event_value (int): Event value that triggers this room state.
        room_state (TektonRoomState): Room state data associated with this pointer.

    """
    def __init__(self):
        self.event_value = 0
        self.room_state = None

    @property
    def pointer_code(self):
        return b'\x12\xe6'


class TektonRoomSpecialStatePointer(TektonRoomStatePointer):
    """Class that represents a special state pointer in room header data. So far I have only encountered a pointer like
        this in Landing Site's room header data. It has a pointer to a room state, but not an event value. I do not
        know what this is for.

    Attributes:
        room_state (TektonRoomState): Room state data associated with this pointer.

    """
    def __init__(self):
        self.room_state = None

    @property
    def pointer_code(self):
        return b'\x69\xe6'


class TektonRoomState:
    """An object that holds information about a single state for a room. This includes things like what tileset it uses,
        what music plays in the room, the scroll speed of the background, etc.

    Attributes:
        tileset (TileSet): Which tileset the room's tiles use when in this state.
        songset (SongSet): Which group of songs this room uses when in this state.
        song_play_index (SongPlayIndex): Which index of songset to play when in this state.
        fx_pointer (int): Address in FX bank where the FX / Layer 3 data for this room state is stored.
        enemy_set_pointer (int): Address in enemy set bank where the enemy set for this room state is stored.
        enemy_gfx_pointer (int): Address in enemy graphics data bank where the enemy graphics for this room state are
            stored.
        background_x_scroll (int): Speed and direction of background x scroll.
        background_y_scroll (int): Speed and direction of background y scroll.
        room_scrolls_pointer (int): Address in room scrolls bank where the scroll data for this room state are stored.
        unused_pointer (int): Two-byte pointer which is supposedly unused.  TODO: Verify this is not used and remove
        main_asm_pointer (int): Address to main ASM routine for this room when in this state.
        setup_asm_pointer (int): Address to setup ASM routine for this room when in this state.
        tiles (TektonTileGrid): Level data when room is in this state.

    """
    def __init__(self):
        self.tileset = TileSet.CRATERIA_CAVE
        self.songset = SongSet.INTRO
        self.song_play_index = SongPlayIndex.NO_CHANGE
        self.fx_pointer = 0
        self.enemy_set_pointer = 0
        self.enemy_gfx_pointer = 0
        self.background_x_scroll = 0
        self.background_y_scroll = 0
        self.room_scrolls_pointer = 0
        self.unused_pointer = 0
        self.main_asm_pointer = 0
        self.plm_set_pointer = 0
        self.background_pointer = 0
        self.setup_asm_pointer = 0
        self.tiles = None
        self._level_data_address = 0

    @property
    def level_data_address(self):
        """int: Get or set the PC address in the ROM where this room's level data can be found."""
        return self._level_data_address

    @level_data_address.setter
    def level_data_address(self, new_address):
        if not isinstance(new_address, int):
            raise TypeError(
                "Room level data address must be of type int. "
                "You can set a hex value using int hex notation, e.g. 0x21bcd2"
            )
        if new_address < 0:
            raise ValueError("Room level data address must be a positive number.")
        self._level_data_address = new_address
