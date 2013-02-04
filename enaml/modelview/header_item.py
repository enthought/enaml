#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Property

from .enums import ItemFlag
from .item import Item


class HeaderItem(Item):
    """ An `Item` class which acts as a header in an item view.

    """
    #: The text to display in the header.
    text = Unicode

    #: By default, a header's data comes from its `text` or `name`.
    data = Property(
        fget=lambda self: self.text or self.name,
        fset=lambda self, value: setattr(self, 'text', value),
    )

    #: By default, a header item is enabled.
    flags = ItemFlag.ITEM_IS_ENABLED

