#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_container import WxContainer
from .wx_layout_request import EVT_COMMAND_LAYOUT_REQUESTED
from .wx_single_widget_sizer import wxSingleWidgetSizer
from .wx_widget_component import WxWidgetComponent


class WxWindow(WxWidgetComponent):
    """ A Wx implementation of an Enaml Window.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wx.Frame widget.

        """
        widget = wx.Frame(parent)
        widget.SetSizer(wxSingleWidgetSizer())
        return widget

    def create(self, tree):
        """ Create and initialize the window control.

        """
        super(WxWindow, self).create(tree)
        self.set_title(tree['title'])
        self.set_initial_size(tree['initial_size'])
        self.set_modality(tree['modality'])
        self.widget().Bind(wx.EVT_CLOSE, self.on_close)

    def init_layout(self):
        """ Perform the layout initialization for the window control.

        """
        super(WxWindow, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, WxContainer):
                widget.GetSizer().Add(child.widget())
                self._update_client_size_hints()
                break
        widget.Bind(EVT_COMMAND_LAYOUT_REQUESTED, self.on_layout_requested)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _update_client_size_hints(self):
        """ A private method for updating the client size hints.

        This method will pull the current min and max client sizes from
        the window sizer, translate them to window sizes, and update the
        size hints on the window. If the current window size violates
        the new size hints, it will be resized (since Wx is too brain
        dead to handle that itself).

        """
        widget = self.widget()
        sizer = widget.GetSizer()
        min_w, min_h = widget.ClientToWindowSize(sizer.CalcMin())
        max_w, max_h= widget.ClientToWindowSize(sizer.CalcMax())
        widget.SetSizeHints(min_w, min_h, max_w, max_h)
        cur_w, cur_h = widget.GetSize()
        new_w = min(max_w, max(min_w, cur_w))
        new_h = min(max_h, max(min_h, cur_h))
        if cur_w != new_w or cur_h != new_h:
            widget.SetSize(wx.Size(new_w, new_h))

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtWindow.

        """
        for child in self.children():
            if isinstance(child, WxContainer):
                widget = self.widget()
                sizer = widget.GetSizer()
                sizer.Add(child.widget())
                widget.Fit()
                max_size = widget.ClientToWindowSize(sizer.CalcMax())
                widget.SetMaxSize(max_size)
                break

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_close(self, event):
        """ The event handler for the EVT_CLOSE event.

        """
        event.Skip()
        # Make sure the frame is not modal when closing, or no other
        # windows will be unblocked.
        self.widget().MakeModal(False)
        self.send_action('closed', {})

    def on_layout_requested(self, event):
        """ Handle the layout request event from the central widget.

        """
        self._update_client_size_hints()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_close(self, content):
        """ Handle the 'close' action from the Enaml widget.

        """
        self.close()

    def on_action_maximize(self, content):
        """ Handle the 'maximize' action from the Enaml widget.

        """
        self.maximize()

    def on_action_minimize(self, content):
        """ Handle the 'minimize' action from the Enaml widget.

        """
        self.minimize()

    def on_action_restore(self, content):
        """ Handle the 'restore' action from the Enaml widget.

        """
        self.restore()

    def on_action_set_icon(self, content):
        """ Handle the 'set-icon' action from the Enaml widget.

        """
        pass

    def on_action_set_title(self, content):
        """ Handle the 'set-title' action from the Enaml widget.

        """
        self.set_title(content['title'])

    def on_action_set_modality(self, content):
        """ Handle the 'set-modality' action from the Enaml widget.

        """
        self.set_modality(content['modality'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def close(self):
        """ Close the window

        """
        self.widget().Close()

    def maximize(self):
        """ Maximize the window.

        """
        self.widget().Maximize(True)

    def minimize(self):
        """ Minimize the window.

        """
        self.widget().Iconize(True)

    def restore(self):
        """ Restore the window after a minimize or maximize.

        """
        self.widget().Maximize(False)

    def set_icon(self, icon):
        """ Set the window icon.

        """
        pass

    def set_title(self, title):
        """ Set the title of the window.

        """
        self.widget().SetTitle(title)

    def set_initial_size(self, size):
        """ Set the initial size of the window.

        """
        self.widget().SetSize(wx.Size(*size))

    def set_modality(self, modality):
        """ Set the modality of the window.

        """
        if modality == 'non_modal':
            self.widget().MakeModal(False)
        else:
            self.widget().MakeModal(True)

    def set_visible(self, visible):
        """ Set the visibility on the window.

        This is an overridden parent class method to set the visibility
        at a later time, so that layout can be initialized before the
        window is displayed.

        """
        # XXX this could be done better.
        wx.CallAfter(super(WxWindow, self).set_visible, visible)

