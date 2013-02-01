#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode

from .item import Item


class HeaderItem(Item):
    """ A concrete `Item` class which acts like a header.

    This class is one in the set of classes for constructing declarative
    item models for item-based views.

    """
    #: By default, a `HeaderItem` is not selectable.
    selectable = False

    #: By default, a `HeaderItem` is not editable.
    editable =  False

    #: The text to use when displaying this item.
    text = Unicode

    def data(self):
        """ Get the data for the header item.

        Returns
        -------
        result : unicode
            The unicode data to display for the header item. This will
            be the `text` assigned to the item, or it's `name` if the
            text is not provided.

        """
        return self.text or self.name

