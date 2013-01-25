#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from enaml.core.trait_types import CoercingInstance
from enaml.layout.geometry import Size

from .control import Control
from .list_item import ListItem


class ListControl(Control):
    """ A `ListControl` displays a collection `ListItem` children.

    `ListItem` objects are flexible and convenient, but they are also
    fairly heavy weight. `ListControl` is well suited for use when the
    number of `ListItem` children is under ~1000.

    """
    #: The size to render the icons in the list control.
    icon_size = CoercingInstance(Size, (-1, -1))

    #: A read only property which returns the control's list items.
    list_items = Property(depends_on='children')

    #: A list control expands freely in height and width by default.
    hug_width = 'weak'
    hug_height = 'weak'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dictionary for the list control.

        """
        snap = super(ListControl, self).snapshot()
        snap['icon_size'] = self.icon_size
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(ListControl, self).bind()
        self.publish_attributes('icon_size')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_list_items(self):
        """ The getter for the 'list_items' property.

        Returns
        -------
        result : tuple
            The tuple of ListItem children defined for this area.

        """
        isinst = isinstance
        items = (c for c in self.children if isinst(c, ListItem))
        return tuple(items)

