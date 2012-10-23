#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str, Tuple, Range, Enum

from enaml.core.declarative import Declarative


#: A predefined trait which defines a size tuple. A size value of
#: (-1, -1) represents a default size.
SizeTuple = Tuple(Range(low=-1, value=-1), Range(low=-1, value=-1))


#: The standard attributes to proxy for a widget component.
_WIDGET_ATTRS = [
    'enabled', 'visible', 'bgcolor', 'fgcolor', 'font', 'minimum_size',
    'maximum_size', 'show_focus_rect'
]


class WidgetComponent(Declarative):
    """ A Declarative subclass which represents the base of all widgets
    in Enaml.

    """
    #: Whether or not the widget is enabled.
    enabled = Bool(True)

    #: Whether or not the widget is visible.
    visible = Bool(True)

    #: A flag indicating whether or not to show the focus rectangle for
    #: the given widget. This is not necessarily support by all widgets
    #: on all clients. A value of None indicates to use the default as
    #: supplied by the client.
    show_focus_rect = Enum(None, True, False)

    #: The background color of the widget. Supports CSS3 color strings.
    bgcolor = Str

    #: The foreground color of the widget. Supports CSS3 color strings.
    fgcolor = Str

    #: The font used for the widget. Supports CSS font formats.
    font = Str

    #: The minimum size for the widget. The default means that the
    #: client should determine an intelligent minimum size.
    minimum_size = SizeTuple

    #: The maximum size for the widget. The default means that the
    #: client should determine and inteliigent maximum size.
    maximum_size = SizeTuple

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the initial properties for a widget component.

        """
        snap = super(WidgetComponent, self).snapshot()
        get = getattr
        attrs = dict((attr, get(self, attr)) for attr in _WIDGET_ATTRS)
        snap.update(attrs)
        return snap

    def bind(self):
        """ Bind the change handlers for a widget component.

        """
        super(WidgetComponent, self).bind()
        self.publish_attributes(*_WIDGET_ATTRS)

