#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Property, cached_property

from enaml.core.trait_types import CoercingInstance
from enaml.layout.geometry import Size

from .container import Container
from .widget_component import WidgetComponent


class FlowItem(WidgetComponent):
    """ A widget which can be used as an item in a FlowArea.

    A FlowItem is a widget which can be used as a child of a FlowArea
    widget. It can have at most a single child widget which is an
    instance of Container.

    """
    #: The preferred size of this flow item. This size will be used as
    #: the size of the item in the layout, bounded to the computed min
    #: and max size. A size of (-1, -1) indicates to use the size hint
    #: as the preferred size.
    preferred_size = CoercingInstance(Size, (-1, -1))

    #: The alignment of this item in the direction orthogonal to flow.
    align = Enum('leading', 'center', 'trailing')

    #: A read only property which returns the items's flow widget.
    flow_widget = Property(depends_on='children')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the FlowItem.

        """
        snap = super(FlowItem, self).snapshot()
        snap['preferred_size'] = self.preferred_size
        snap['align'] = self.align
        return snap

    def bind(self):
        """ Bind the change handler for the FlowItem.

        """
        super(FlowItem, self).bind()
        self.publish_attributes('preferred_size', 'align')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_flow_widget(self):
        """ The getter for the 'flow_widget' property.

        Returns
        -------
        result : Container or None
            The flow widget for the FlowItem, or None if not provided.

        """
        widget = None
        for child in self.children:
            if isinstance(child, Container):
                widget = child
        return widget

