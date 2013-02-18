#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from atom.api import Bool, Str, Enum, Unicode, Coerced, Instance, observe, null

from enaml.core.declarative import Declarative, d
from enaml.core.messenger import Messenger
from enaml.layout.geometry import Size
from enaml.utils import LoopbackGuard


class Widget(Messenger, Declarative):
    """ The base class of all visible widgets in Enaml.

    """
    #: Whether or not the widget is enabled.
    enabled = d(Bool(True))

    #: Whether or not the widget is visible.
    visible = d(Bool(True))

    #: The background color of the widget. Supports CSS3 color strings.
    bgcolor = d(Str())

    #: The foreground color of the widget. Supports CSS3 color strings.
    fgcolor = d(Str())

    #: The font used for the widget. Supports CSS font formats.
    font = d(Str())

    #: The minimum size for the widget. The default means that the
    #: client should determine an intelligent minimum size.
    minimum_size = d(Coerced(Size, factory=lambda: Size(-1, -1)))

    #: The maximum size for the widget. The default means that the
    #: client should determine and inteliigent maximum size.
    maximum_size = d(Coerced(Size, factory=lambda: Size(-1, -1)))

    #: The tool tip to show when the user hovers over the widget.
    tool_tip = d(Unicode())

    #: The status tip to show when the user hovers over the widget.
    status_tip = d(Unicode())

    #: A flag indicating whether or not to show the focus rectangle for
    #: the given widget. This is not necessarily support by all widgets
    #: on all clients. A value of None indicates to use the default as
    #: supplied by the client.
    show_focus_rect = d(Enum(None, True, False))

    #: A loopback guard which can be used to prevent a notification
    #: cycle when setting attributes from within an action handler.
    loopback_guard = Instance(LoopbackGuard, factory=LoopbackGuard)

    #--------------------------------------------------------------------------
    # Messenger API
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
        return snap

    #--------------------------------------------------------------------------
    # Widget Updates
    #--------------------------------------------------------------------------
    @observe('enabled|visible|bgcolor|fgcolor|font|minimum_size|maximum_size'
             'show_focus_rect|tool_tip|status_tip', regex=True)
    def send_widget_change(self, change):
        """ Send the state change for the widget.

        """
        name = change.name
        if change.old is not null and name not in self.loopback_guard:
            self.send_action('set_' + name, {name: change.new})

    def set_guarded(self, **attrs):
        """ Set attribute values from within a loopback guard.

        This is a convenience method provided for subclasses to set the
        values of attributes from within a loopback guard. This prevents
        the change from being published back to client and reduces the
        chances of getting hung in a feedback loop.

        Parameters
        ----------
        **attrs
            The attributes to set on the widget from within a loopback
            guard context.

        """
        with self.loopback_guard(*attrs):
            for name, value in attrs.iteritems():
                setattr(self, name, value)

