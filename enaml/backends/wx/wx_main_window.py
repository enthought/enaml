#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

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
        self._cached_min = None

    def Add(self, widget):
        """ Adds the given widget to the sizer, removing the old widget
        if present. The old widget is not destroyed.

        """
        self.Clear(deleteWindows=False)
        self._widget = widget
        return super(WXMainWindowSizer, self).Add(widget)

    def CalcMin(self):
        """ Returns the minimum size for the children this sizer is 
        managing. Since the size of the Dialog is managed externally,
        this always returns (-1, -1).

        """
        widget = self._widget
        if widget:
            res = widget.GetMinSize()
        else:
            res = (-1, -1)
        if res != self._cached_min:
            self._cached_min = res
            self.SetMinFrameSize(res)
        return res
    
    def RecalcSizes(self):
        """ Resizes the child to fit the available space of the window.

        """
        widget = self._widget
        if widget:
            widget.SetSize(self.GetSize())
                
    def SetMinFrameSize(self, size):
        """ Sets the minimum size allowed of the frame. This is called
        as necessary when the sizing of the frame's contents changes.
        The given size should not include any allowance for frame 
        decorations as that is accounted for automatically.

        """
        frame = self.GetContainingWindow()
        f_width, f_height = frame.GetSizeTuple()
        c_width, c_height = frame.GetClientSizeTuple()
        d_width = f_width - c_width
        d_height = f_height - c_height
        n_width = size[0] + d_width
        n_height = size[1] + d_height
        frame.SetMinSize((n_width, n_height))


class  WXMainWindow(WXWindow, AbstractTkMainWindow):
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

