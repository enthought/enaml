#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_control import WxControl
from .wx_single_widget_sizer import wxSingleWidgetSizer

from enable.api import Window as EnableWindow


class WxEnableCanvas(WxControl):
    """ A Wx implementation of an Enaml EnableCanvas.

    """
    #: Internal storage for the enable component.
    _component = None

    #: Internal storage for the enable window.
    _window = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying widget.

        """
        widget = wx.Panel(parent)
        sizer = wxSingleWidgetSizer()
        widget.SetSizer(sizer)
        return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(WxEnableCanvas, self).create(tree)
        self._component = tree['component']

    def init_layout(self):
        """ Initialize the layout of the underlying widget.

        """
        super(WxEnableCanvas, self).init_layout()
        self.refresh_enable_widget()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_component(self, content):
        """ Handle the 'set_component' action from the Enaml widget.

        """
        self._component = content['component']
        self.refresh_enable_widget()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def refresh_enable_widget(self):
        """ Create the enable widget and update the underlying control.

        """
        widget = self.widget()
        widget.Freeze()
        component = self._component
        if component is not None:
            self._window = EnableWindow(widget, component=component)
            enable_widget = self._window.control
        else:
            self._window = None
            enable_widget = None
        widget.GetSizer().Add(enable_widget)
        widget.Thaw()

