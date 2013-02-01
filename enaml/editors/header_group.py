#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str

from enaml.core.declarative import Declarative

from .header_item import HeaderItem


class HeaderGroup(Declarative):
    """ A class for grouping header items in an item-based view.

    A `HeaderGroup` can be used in conjunction with `HeaderItem` to
    declaratively create item-based views. The `name` of the header
    group is used find the matchin `EditGroup` on a `ModelEditor`

    """
    #: The background color of the header group. Supports CSS3 color
    #: strings. If a `HeaderItem` does not define a background, it will
    #: inherit this background color.
    background = Str

    #: The foreground color of the header group. Supports CSS3 color
    #: strings. If a `HeaderItem` does not define a foreground, it will
    #: inherit this foreground color.
    foreground = Str

    #: The font of the header group. Supports CSS3 shorthand font
    #: strings. If a `HeaderItem` does not define a font, it will
    #: inherit this font.
    font = Str

    #: Whether or not the header group is visible in the view.
    visible = Bool(True)

    def header_items(self):
        """ Get the header items defined on this group.

        Returns
        -------
        result : generator
            A generator which will yield the children of the group
            which are instances of `HeaderItem`.

        """
        for child in self.children:
            if isinstance(child, HeaderItem):
                yield child

