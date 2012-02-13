#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_window import WXWindow

from ..dialog import AbstractTkDialog


class WXDialogSizer(wx.PySizer):
    """ A custom wx Sizer for use in the WXDialog. This sizers expands
    its child to fit the allowable space, regardless of the settings on
    the child settings. This is similar to how central widgets behave 
    in a WXMainWindow. 

    There can only be one widget in this sizer at a time and it should
    be added via the .Add(...) method. Old items will be removed 
    automatically (but not destroyed).

    """
    def Add(self, widget):
        """ Adds the given widget to the sizer, removing the old widget
        if present. The old widget is not destroyed.

        """
        self.Clear(deleteWindows=False)
        return super(WXDialogSizer, self).Add(widget)

    def CalcMin(self):
        """ Returns the minimum size for the children this sizer is 
        managing. Since the size of the Dialog is managed externally,
        this always returns (-1, -1).

        """
        return (-1, -1)
    
    def RecalcSizes(self):
        """ Resizes the child to fit the available space of the scroll
        area.

        """
        children = self.GetChildren()
        if len(children) > 0:
            widget = children[0].GetWindow()
            if widget:
                widget.SetSize(self.GetSize())


class WXDialog(WXWindow, AbstractTkDialog):
    """ A wxPython implementation of a Dialog.

    WXDialog uses a wx.Dialog to create a simple top-level dialog.

    """
    #---------------------------------------------------------------------------
    # Setup methods
    #---------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.Dialog control.

        """
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        self.widget = wx.Dialog(parent, style=style)
        self.widget.SetSizer(WXDialogSizer())

    def initialize(self):
        """ Intializes the attributes on the wx.Dialog.

        """
        super(WXDialog, self).initialize()
        self.widget.Bind(wx.EVT_CLOSE, self._on_close)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def accept(self):
        """ Close the dialog and set the result to 'accepted'.

        """
        self._close_dialog('accepted')

    def reject(self):
        """ Close the dialog and set the result to 'rejected'.

        """
        self._close_dialog('rejected')

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def _on_close(self, event):
        """ Destroy the dialog to handle the EVT_CLOSE event. This will 
        happen if the user clicks on the 'X'. This is equivalent to
        calling 'reject()'.

        """
        self.reject()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def update_central_widget(self):
        """ Updates the central widget in the dialog with the value from
        the shell object.

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

    def set_visible(self, visible):
        """ Overridden from the parent class to properly launch and close 
        the dialog.

        """
        widget = self.widget
        shell = self.shell_obj
        if visible:
            shell._active = True
            shell.opened()
            # wx cannot distinguish between app modal and 
            # window modal, so we only get one kind.
            widget.ShowModal()
        else:
            self.reject()
    
    #--------------------------------------------------------------------------
    # Auxiliary Methods 
    #--------------------------------------------------------------------------
    def _close_dialog(self, result):
        """ Destroy the dialog, fire events, and set status attributes.

        """
        # Explicitly Destroy the dialog or the wxApp won't properly exit.
        if self.widget:
            self.widget.Destroy()
        
        shell = self.shell_obj
        shell._result = result
        shell._active = False
        shell.closed(result)

