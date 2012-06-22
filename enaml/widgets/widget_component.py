#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str, Tuple, Range

from .messenger_widget import MessengerWidget


#: A predefined trait which defines a size tuple. A size value of
#: (-1, -1) represents a default size.
SizeTuple = Tuple(Range(low=-1, value=-1), Range(low=-1, value=-1))


#: The standard attributes to proxy for a widget component.
_WIDGET_PROXY_ATTRS = [
    'enabled', 'visible', 'bgcolor', 'fgcolor', 'font', 'size_hint',
    'min_size', 'max_size'
]


class WidgetComponent(MessengerWidget):
    """ A MessengerWidget subclass which represents the base of all
    widgets in Enaml.

    """
    #: Whether or not the widget is enabled.
    enabled = Bool(True)

    #: Whether or not the widget is visible.
    visible = Bool(True)

    #: The background color of the widget. Supports CSS color formats.
    bgcolor = Str

    #: The foreground color of the widget. Supports CSS color formats.
    fgcolor = Str

    #: The font used for the widget. Supports CSS font formats.
    font = Str

    #: The size hint for the widget. The default means that the client
    #: should determine the size hint. This is normally sufficient, but
    #: can be overridden to supply custom size hinting.
    size_hint = SizeTuple

    #: The minimum size for the widget. The default means that the
    #: client should determine an intelligent minimum size.
    min_size = SizeTuple

    #: The maximum size for the widget. The default means that the
    #: client should determine and inteliigent maximum size.
    max_size = SizeTuple

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def initial_attrs(self):
        """ Return the attr initialization dict for a widget component.

        """
        super_attrs = super(WidgetComponent, self).initial_attrs()
        get = getattr
        attrs = dict((attr, get(self, attr)) for attr in _WIDGET_PROXY_ATTRS)
        super_attrs.update(attrs)
        return super_attrs

    def bind(self):
        """ Bind the change handlers for the widget component.

        """
        super(WidgetComponent, self).bind()
        self.default_send(*_WIDGET_PROXY_ATTRS)

