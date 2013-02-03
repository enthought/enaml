#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str

from enaml.core.declarative import Declarative

from .item import Item


class HeaderGroup(Declarative):
    """ A class for grouping header items in an item based view.

    """
    #: The background color of the header group. Supports CSS3 color
    #: strings.
    background = Str

    #: The foreground color of the header group. Supports CSS3 color
    #: strings.
    foreground = Str

    #: The font of the header group. Supports CSS3 shorthand font
    #: strings.
    font = Str

    def items(self):
        """ Get the items defined on this header group.

        Returns
        -------
        result : generator
            A generator which will yield the group children which are
            instances of `Item`.

        """
        for child in self.children:
            if isinstance(child, Item):
                yield child

