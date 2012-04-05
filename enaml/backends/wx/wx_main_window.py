#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_widget_component import EVT_MIN_SIZE
from .wx_window import WXWindow

from ...components.main_window import AbstractTkMainWindow


class WXMainWindowSizer(wx.PySizer):
    """ A custom wx Sizer for use in the WXMainWindow. This sizer expands
    its child to fit the allowable space, but respects the minimum size
    of the child.

    There can only be one widget in this sizer at a time and it should
    be added via the .Add(...) method. Old items will be removed 
    automatically (but not destroyed).

    """
    def __init__(self, *args, **kwargs):
        super(WXMainWindowSizer, self).__init__(*args, **kwargs)
        self._widget = None
        self._min_size = None

    def OnWidgetMinSize(self, event):
        """ An event handler which is called when the min size is set 
        on the central widget. It updates the internal cached min size
        and updates the frame sizing.

        """
        self._min_size = self._widget.GetMinSize()
        self.UpdateFrameSizing()
        event.Skip()

    def Add(self, widget):
        """ Adds the given widget to the sizer, removing the old widget
        if present. The old widget is not destroyed.

        """
        self.Clear(deleteWindows=False)
        old_widget = self._widget
        if old_widget is not None:
            old_widget.Unbind(EVT_MIN_SIZE, handler=self.OnWidgetMinSize)
        widget.Bind(EVT_MIN_SIZE, self.OnWidgetMinSize)
        self._widget = widget
        self._min_size = widget.GetMinSize()
        res = super(WXMainWindowSizer, self).Add(widget)
        self.UpdateFrameSizing()
        return res

    def CalcMin(self):
        """ Returns the computed minimum size for the for the frame.

        """
        return self._min_size
    
    def RecalcSizes(self):
        """ Resizes the child to fit the available space of the window.

        """
        widget = self._widget
        if widget:
            widget.SetSize(self.GetSize())
                
    def UpdateFrameSizing(self):
        """ Sets the minimum size allowed of the frame and resizes it 
        if necessary. This is called whenever the minimum size of the
        central widget changes.

        """
        frame = self.GetContainingWindow()
        min_width, min_height = self._min_size
        frame_width, frame_height = frame.GetSizeTuple()
        client_width, client_height = frame.GetClientSizeTuple()
        delta_width = frame_width - client_width
        delta_height = frame_height - client_height
        new_min_width = min_width + delta_width
        new_min_height = min_height + delta_height
        frame.SetMinSize((new_min_width, new_min_height))
        if new_min_width > frame_width or new_min_height > frame_height:
            resize_width = max(new_min_width, frame_width)
            resize_height = max(new_min_height, frame_height)
            frame.SetSize((resize_width, resize_height))


class WXMainWindow(WXWindow, AbstractTkMainWindow):
    """ A Wx implementation of a MainWindow.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.Frame with an appropriate main
        window sizer.

        """
        self.widget = wx.Frame(parent)
        self.widget.SetSizer(WXMainWindowSizer())

    def initialize(self):
        """ Intializes the attributes on the wx.Frame.

        """
        super(WXMainWindow, self).initialize()
        shell = self.shell_obj
        self.set_menu_bar(shell.menu_bar)

    def bind(self):
        """ Bind the signal handlers for the wx.Frame.

        """
        super(WXMainWindow, self).bind()
        self.widget.Bind(wx.EVT_CLOSE, self._on_close)
    
    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def shell_menu_bar_changed(self, menu_bar):
        """ Update the menu bar of the window with the new value from
        the shell object.

        """
        self.set_menu_bar(menu_bar)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def _on_close(self, event):
        """ Emits the closed event on the shell object when the main 
        window is closed.

        """
        event.Skip()
        self.shell_obj.closed()
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_central_widget(self, central_widget):
        """ Sets the central widget in the window with the given value.

        """
        # It's possible for the central widget component to be None.
        # This must be allowed since the central widget may be generated
        # by an Include component, in which case it will not exist 
        # during initialization. However, we must have a central widget
        # for the Dialog, and so we just fill it with a dummy widget.
        central_widget = self.shell_obj.central_widget
        if central_widget is None:
            child_widget = wx.Panel(self.widget)
        else:
            child_widget = central_widget.toolkit_widget
        self.widget.GetSizer().Add(child_widget)

    def set_menu_bar(self, menu_bar):
        """ Updates the menu bar in the main window with the given Enaml
        MenuBar instance.

        """
        if menu_bar is not None:
            self.widget.SetMenuBar(menu_bar.toolkit_widget)
        else:
            self.widget.SetMenuBar(None)

    def set_visible(self, visible):
        """ Overridden from the parent class to raise the window to
        the front if it should be shown.

        """
        widget = self.widget
        if visible:
            widget.Show(True)
            widget.Raise()
        else:
            widget.Show(False)

