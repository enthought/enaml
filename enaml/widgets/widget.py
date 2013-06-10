#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str, Tuple, Range, Enum, Unicode, List, Any

from enaml.core.trait_types import EnamlEvent
from enaml.core.messenger import Messenger


#: A predefined trait which defines a size tuple. A size value of
#: (-1, -1) represents a default size.
SizeTuple = Tuple(Range(low=-1, value=-1), Range(low=-1, value=-1))


class Widget(Messenger):
    """ The base class of all visible widgets in Enaml.

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

    #: The tool tip to show when the user hovers over the widget.
    tool_tip = Unicode

    #: The status tip to show when the user hovers over the widget.
    status_tip = Unicode

    #: Whether or not the widget can be dropped on
    accept_drops = Bool(False)

    #: Whether or not the widget can be dragged
    accept_drags = Bool(False)

    #: The mime-type associated with the drag
    drag_type = Str

    #: The data to be dragged
    drag_data = Any

    #: The mime types that the widget allows to be dropped on itself
    drop_types = List(Str)

    #: Fired when something is dropped on the widget
    dropped = EnamlEvent

    #: Fired when the mouse is pressed on a widget
    mouse_pressed = EnamlEvent

    #: Fired when the mouse is moved on a widget
    mouse_moved = EnamlEvent

    #: Fired when the mouse is released on a widget
    mouse_released = EnamlEvent

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        snap = super(Widget, self).snapshot()
        snap['enabled'] = self.enabled
        snap['visible'] = self.visible
        snap['bgcolor'] = self.bgcolor
        snap['fgcolor'] = self.fgcolor
        snap['font'] = self.font
        snap['minimum_size'] = self.minimum_size
        snap['maximum_size'] = self.maximum_size
        snap['show_focus_rect'] = self.show_focus_rect
        snap['tool_tip'] = self.tool_tip
        snap['status_tip'] = self.status_tip
        snap['accept_drops'] = self.accept_drops
        snap['accept_drags'] = self.accept_drags
        snap['drag_type'] = self.drag_type
        snap['drag_data'] = self.drag_data
        snap['drop_types'] = self.drop_types
        return snap

    def bind(self):
        """ Bind the change handlers for a widget component.

        """
        super(Widget, self).bind()
        attrs = (
            'enabled', 'visible', 'bgcolor', 'fgcolor', 'font',
            'minimum_size', 'maximum_size', 'show_focus_rect',
            'tool_tip', 'status_tip', 'accept_drops', 'accept_drags',
            'drag_type', 'drag_data', 'drop_types',
        )
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_dropped(self, content):
        """ Handle the 'dropped' action from the client widget.

        """
        self.dropped(content['data'])

    def on_action_mouse_pressed(self, content):
        """ Handle the 'mouse_pressed' action from the client widget.

        """
        self.mouse_pressed(content)

    def on_action_mouse_moved(self, content):
        """ Handle the 'mouse_moved' action from the client widget.

        """
        self.mouse_moved(content)

    def on_action_mouse_released(self, content):
        """ Handle the 'mouse_released' action from the client widget.

        """
        self.mouse_released(content)
