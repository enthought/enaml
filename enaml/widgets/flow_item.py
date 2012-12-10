#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Range, Property, cached_property

from enaml.core.trait_types import CoercingInstance
from enaml.layout.geometry import Size

from .container import Container
from .widget import Widget


class FlowItem(Widget):
    """ A widget which can be used as an item in a FlowArea.

    A FlowItem is a widget which can be used as a child of a FlowArea
    widget. It can have at most a single child widget which is an
    instance of Container.

    """
    #: The preferred size of this flow item. This size will be used as
    #: the size of the item in the layout, bounded to the computed min
    #: and max size. A size of (-1, -1) indicates to use the widget's
    #: size hint as the preferred size.
    preferred_size = CoercingInstance(Size, (-1, -1))

    #: The alignment of this item in the direction orthogonal to the
    #: layout flow.
    align = Enum('leading', 'trailing', 'center')

    #: The stretch factor for this item in the flow direction, relative
    #: to other items in the same line. The default is zero which means
    #: that the item will not expand in the direction orthogonal to the
    #: layout flow.
    stretch = Range(low=0, value=0)

    #: The stretch factor for this item in the orthogonal direction
    #: relative to other items in the layout. The default is zero
    #: which means that the item will not expand in the direction
    #: orthogonal to the layout flow.
    ortho_stretch = Range(low=0, value=0)

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
        snap['stretch'] = self.stretch
        snap['ortho_stretch'] = self.ortho_stretch
        return snap

    def bind(self):
        """ Bind the change handler for the FlowItem.

        """
        super(FlowItem, self).bind()
        attrs = ('preferred_size', 'align', 'stretch', 'ortho_stretch')
        self.publish_attributes(*attrs)

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

