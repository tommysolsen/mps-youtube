"""
    An object used to reference items of a ListView
"""

from typing import Mapping

class ListViewItem:
    """ Base class for items
        Used by Listview
    """
    data = None

    def __init__(self, data: Mapping[str, object]):
        self.data = data

    def __getattr__(self, key: str) -> object:
        return self.data[key] if key in self.data.keys() else None

    def get_with_default(self, key: str, default: object) -> object:
        """ Gets an attribute from this object or returns default """
        val = self.__getattr__(key)
        return val if val else default

    def length(self, _=0):
        # pylint: disable=R0201
        """ Returns length of ListViewItem
            A LVI has to return something for length
            even if the item does not have one.
        """
        return 0
