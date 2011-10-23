#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Instance, DelegatesTo

from .style_sheet import StyleSheet
from .style_node import StyleNode
from .style_manager import StyleManager


class StyleMixin(HasTraits):

    style_sheet = Instance(StyleSheet, ())

    style_node = Instance(StyleNode, ())

    style_manager = Instance(StyleManager)

    def _style_manager_default(self):
        return StyleManager(component=self)

    #--------------------------------------------------------------------------
    # Style Value Delegates
    #--------------------------------------------------------------------------
    #: The alignment of a widget in its parent layout
    alignment = DelegatesTo('style_node')

    #: The foreground color of a widget. This is usually text color.
    fgcolor = DelegatesTo('style_node')

    #: The background color of a widget.
    bgcolor = DelegatesTo('style_node')

    #: The font to use for the widget.
    font = DelegatesTo('style_node')

    #: The margins to place around a layout.
    margins = DelegatesTo('style_node')

    ##: The suggested (w, h) size of the widget.
    #size_hint = DelegatesTo('style_node')

    #: How the widget should be resized when placed in a layout.
    size_policy = DelegatesTo('style_node')

    #: The interelement spacing in a layout
    spacing = DelegatesTo('style_node')

    #: The stretch factor to use when adding the widget to a layout
    stretch = DelegatesTo('style_node')

    #: The string name of the style class to use for this node.
    style_class = DelegatesTo('style_node')

