"""Tekton Room Dict

This module implements an object that stores and organizes the rooms in a Tekton project. Rooms are indexed by their
header addresses. For convenience, you can add a room without explicitly referencing its index.

Classes:
    TektonRoomDict: Dictionary-like object that sorts and organizes TektonRoom objects.
    DuplicateRoomError: Exception raised when the user tries to add a new room whose header already exists

"""

class TektonRoomDict:
    """A dictionary-like object that sorts and organizes TektonRoom objects.

    Attributes:
        (none)
    """

    def __init__(self):
        self._rooms = []

    def __getitem__(self, item):
        """Returns a TektonRoom whose header attribute matches the item arg, or None if no such room exists.

        Args:
            item (int): Header address of the room you want.

        Returns:
            TektonRoom : Room whose header matches item, or None if no such room exists.

        """

        for room in self._rooms:
            if room.header == item:
                return room
        return None

    def add_room(self, new_room):
        """Adds a room to the TektonRoomDict.

        If the TektonRoomDict already contains a room with the same header address as new_room, this function will
        raise a ValueError.

        Args:
            new_room (TektonRoom): Room to be added to the TektonRoomDict.

        """

        if new_room.header in self.keys():
            raise DuplicateRoomError(
                "There is already a room with header {} in the project!".format(hex(new_room.header))
            )
        self._rooms.append(new_room)

    def keys(self):
        """Returns a sorted list of header addresses for rooms in this TektonRoomDict.

        Returns:
            list : Header addresses of all the rooms in this TektonRoomDict.
        """

        return sorted([room.header for room in self._rooms])

    def items(self):
        """Returns the header addresses and TektonRoom objects from this dict as key-value pairs.

        Returns:
            iterable : Iterator yielding a typle of (header address, TektonRoom object)
        """

        for key in self.keys():
            yield key, self[key]


class DuplicateRoomError(Exception):
    """Raised when the user attempts to add a room whose header already exists in the TektonRoomDict."""
    pass
