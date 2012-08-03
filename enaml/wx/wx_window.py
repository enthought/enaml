#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_widget_component import WxWidgetComponent


class WxWindowSizer(wx.PySizer):
    """ A custom wx Sizer for use in the WxWindow. 

    There can only be one widget in this sizer at a time and it should
    be added via the .Add(...) method. Old items will be removed 
    automatically (but not destroyed).

    """
    _default_size = wx.Size(-1, -1)

    _widget = None

    def CalcMax(self):
        """ A method to compute the maximum size allowed by the sizer.

        This is not a native wx sizer method, but is included for 
        convenience.

        """
        widget = self._widget
        if not widget:
            return self._default_size
        return widget.GetMaxSize()

    def Add(self, widget):
        """ Adds the given widget to the sizer, removing the old widget
        if present. The old widget is not destroyed.

        """
        self.Clear(deleteWindows=False)
        self._widget = widget
        return super(WxWindowSizer, self).Add(widget)

    def CalcMin(self):
        """ Returns the minimum size for the children this sizer is 
        managing. Since the size of the Dialog is managed externally,
        this always returns (-1, -1).

        """
        widget = self._widget
        if not widget:
            return self._default_size
        return widget.GetEffectiveMinSize()

    def RecalcSizes(self):
        """ Resizes the child to fit the available space of the window.

        """
        widget = self._widget
        if widget:
            widget.SetSize(self.GetSize())


class WxWindow(WxWidgetComponent):
    """ A Wx implementation of an Enaml Window.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wx.Frame widget.

        """
        return wx.Frame(parent)

    def create(self, tree):
        """ Create and initialize the window control.

        """
        super(WxWindow, self).create(tree)
        self.set_title(tree['title'])
        self.set_initial_size(tree['initial_size'])

    def init_layout(self):
        """ Perform the layout initialization for the window control.

        """
        # A Window is a top-level component and `init_layout` is called 
        # bottom-up, so the layout for all of the children has already
        # taken place. This is the proper time to grab the central 
        # widget child, stick it the sizer, and fit the window.
        children = self.children
        if children:
            child_widget = children[0].widget
            sizer = WxWindowSizer()
            sizer.Add(child_widget)
            widget = self.widget
            widget.SetSizerAndFit(sizer)
            max_size = widget.ClientToWindowSize(sizer.CalcMax())
            widget.SetMaxSize(max_size)

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
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def close(self):
        """ Close the window

        """
        self.widget.Close()

    def maximize(self):
        """ Maximize the window.

        """
        self.widget.Maximize(True)

    def minimize(self):
        """ Minimize the window.

        """
        self.widget.Iconize(True)

    def restore(self):
        """ Restore the window after a minimize or maximize.

        """
        self.widget.Maximize(False)

    def set_icon(self, icon):
        """ Set the window icon.

        """
        pass

    def set_title(self, title):
        """ Set the title of the window.

        """
        self.widget.SetTitle(title)

    def set_initial_size(self, size):
        """ Set the initial size of the window.

        """
        self.widget.SetSize(wx.Size(*size))

