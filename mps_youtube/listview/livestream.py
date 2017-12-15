"""
    Represents a LiveStream ListViewItem
"""
from .base import ListViewItem
from .. import util


class ListLiveStream(ListViewItem):
    """ Class exposing necessary components of a live stream """
    # pylint: disable=unused-argument
    def ytid(self, lngt: int = 10) -> str:
        """ Exposes ytid(string) """
        return self.data.get("id").get("videoId")

    def ret(self) -> str:
        """ Returns content.video compatible tuple """
        return (self.ytid(), self.title(), self.length())

    def title(self, lngt: int = 10) -> str:
        """ exposes title """
        return util.uea_pad(lngt, self.data.get("snippet").get("title"))

    def description(self, lngt: int = 10) -> str:
        """ exposes description """
        return util.uea_pad(lngt, self.data.get("snippet").get("description"))

    @staticmethod
    def return_field() -> str:
        """ ret """
        return "ret"
