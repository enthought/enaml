#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Range, Property, cached_property

from enaml.core.trait_types import CoercingInstance
from enaml.layout.geometry import Box

from .constraints_widget import ConstraintsWidget
from .flow_item import FlowItem


class FlowArea(ConstraintsWidget):
    """ A widget which lays out its children in flowing manner, wrapping
    around at the end of the available space.

    """
    #: The flow direction of the layout.
    direction = Enum(
        'left_to_right', 'right_to_left', 'top_to_bottom', 'bottom_to_top'
    )

    #: The alignment of a line of items within the layout.
    align = Enum('leading', 'trailing', 'center', 'justify')

    #: The amount of horizontal space to place between items.
    horizontal_spacing = Range(low=0, value=10)

    #: The amount of vertical space to place between items.
    vertical_spacing = Range(low=0, value=10)

    #: The margins to use around the outside of the flow area.
    margins = CoercingInstance(Box, (10, 10, 10, 10))

    #: A read only property which returns the area's flow items.
    flow_items = Property(depends_on='children')

    #: A FlowArea expands freely in width and height by default.
    hug_width = 'ignore'
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the FlowArea.

        """
        snap = super(FlowArea, self).snapshot()
        snap['direction'] = self.direction
        snap['align'] = self.align
        snap['horizontal_spacing'] = self.horizontal_spacing
        snap['vertical_spacing'] = self.vertical_spacing
        snap['margins'] = self.margins
        return snap

    def bind(self):
        """ Bind the change handler for the FlowItem.

        """
        super(FlowArea, self).bind()
        attrs = (
            'direction', 'align', 'horizontal_spacing','vertical_spacing',
            'margins',
        )
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_flow_items(self):
        """ The getter for the 'flow_items' property.

        Returns
        -------
        result : tuple
            The tuple of FlowItem children defined for this area.

        """
        isinst = isinstance
        items = (c for c in self.children if isinst(c, FlowItem))
        return tuple(items)

