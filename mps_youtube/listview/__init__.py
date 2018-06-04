"""
    Describes a PaginatedContent version of the standard ListView
"""
import re
import math
from typing import Set, Callable

from .. import c, g, util, content
from .base import ListViewItem
from .user import ListUser
from .livestream import ListLiveStream
from .songtitle import ListSongtitle

class ListView(content.PaginatedContent):
    """ Content Agnostic Numbered List

        This class, using ListViewItems as abstractions you can
        give it a list of data and which columns to show and it will
        show it.

        Todo:
            Currently we rely on the commands/play code to send information
            about which elements are being picked.

        Attributes:
            func        The function that will be run on the selected items
            objects     List of objects(or a ContentQuery object)
            columns     A list of Hashes containing information about which
                        columns to show
            page        Current Page

        Column format:
            {"name": "idx", "size": 3, "heading": "Num"}
            name:    The method name that will be called from the ListViewItem
            size:    How much size is allocated to the columns,
                     see ListView.content for more information about
                     the dynamic options
            heading: The text shown in the header

            "idx" is generated in the content function, not by the ListViewItem
    """
    func = None
    objects = None
    columns = None
    page = 0

    def __init__(self,
                 columns: Set[str],
                 objects: Set[ListViewItem],
                 function_call: Callable[[Set[object]], None] = None):
        self.func = function_call
        self.objects = objects
        self.columns = columns
        self.object_type = None

        # Ensure single type of object
        types = len(set([obj.__class__ for obj in objects]))
        if types == 0:
            raise BaseException("No objects in list")
        if types > 1:
            raise BaseException("More than one kind of objects in list")

        self.object_type = [obj.__class__ for obj in objects][0]

    def numPages(self) -> int:
        """ Returns # of pages """
        return max(1, math.ceil(len(self.objects) / util.getxy().max_results))

    def getPage(self, page: int):
        self.page = page
        return self.content()

    def _page_slice(self) -> list:
        chgt = util.getxy().max_results
        return slice(self.page * chgt, (self.page+1) * chgt)

    def content(self) -> str:
        """ Generates content

            ===============
            Dynamic fields
            ===============

            Column.size may instead of an integer be a string
            containing either "length" or "remaining".

            Length is for time formats like 20:40
            Remaining will allocate all remaining space to that
            column.

            TODO: Make it so set columns can set "remaining" ?
        """
        # Sum all ints, deal with strings later
        # Gets max width of screen
        # Subtracts all known widths(ints)
        # Subtracts 1 char for each column separator
        remaining = util.getxy().width \
                  - sum(map(lambda x: x['size'] if x['size'] and x['size'].__class__ == int else 0,
                            self.columns) + 1) \
                  - len(self.columns)
        lengthsize = 0
        if "length" in [x['size'] for x in self.columns]:
            max_l = max((getattr(x, "length")() for x in self.objects))
            lengthsize = 8 if max_l > 35999 else 7
            lengthsize = 6 if max_l < 6000 else lengthsize

        for col in self.columns:
            if col['size'] == "remaining":
                col['size'] = remaining - lengthsize
            if col['size'] == "length":
                col['size'] = lengthsize

        for num, column in enumerate(self.columns):
            column['idx'] = num
            column['sign'] = "-" if not column['name'] == "length" else ""

        fmt = ["%{}{}s  ".format(x['sign'], x['size']) for x in self.columns]
        fmtrow = fmt[0:1] + ["%s  "] + fmt[2:]
        fmt, fmtrow = "".join(fmt).strip(), "".join(fmtrow).strip()
        out = "\n" \
            + (c.ul + fmt % tuple([x['heading'][:x['size']] for x in self.columns]) + c.w) \
            + "\n"

        for num, obj in enumerate(self.objects[self._page_slice()]):
            col = (c.r if num % 2 == 0 else c.p)

            data = []
            for column in self.columns:
                fieldsize, field = column['size'], column['name']
                if field == "idx":
                    data.append("%2d" % (num + (util.getxy().max_results * self.page) + 1))
                else:
                    field = getattr(obj, field)(fieldsize)
                    field = str(field) if field.__class__ != str else field
                    if len(field) > fieldsize:
                        field = field[:fieldsize]
                    else:
                        field = field + (" " * (fieldsize - len(field)))
                    data.append(field)
            line = col + (fmtrow % tuple(data)) + c.w
            out += line + "\n"

        return out

    def _play(self, _, choice, __):  # pre, choice, post
        """ Handles what happends when a user selects something from the list
            Currently this functions hooks into commands/play
        """

        uids = []
        for splitted_choice in choice.split(","):
            cho = splitted_choice.strip()
            if cho.isdigit():
                uids.append(int(cho) - 1)
            else:
                cho = cho.split("-")
                if cho[0].isdigit() and cho[1].isdigit():
                    uids += list(range(int(cho[0]) - 1, int(cho[1])))

        var = getattr(self.object_type, "return_field")()
        self.func([getattr(self.objects[x], var)() for x in uids])
