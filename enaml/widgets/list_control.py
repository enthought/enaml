#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List, Instance

from .control import Control
from .list_item import ListItem


class ListControl(Control):
    """ A `ListControl` displays a collection `ListItem` objects.

    `ListItem` objects are flexible and convenient, but they are also
    fairly heavy weight. `ListControl` is well suited for use with data
    models under ~1000 items.

    """
    items = List(Instance(ListItem))

    hug_width = 'weak'
    hug_height = 'weak'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dictionary for the list control.

        """
        snap = super(ListControl, self).snapshot()
        snap['items'] = [item.snapshot() for item in self.items]
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(ListControl, self).bind()

