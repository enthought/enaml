#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_window import WXWindow

from ...components.dialog import AbstractTkDialog


DIALOG_RETCODE_MAP = {
    wx.ID_OK: 'accepted',
    wx.ID_CANCEL: 'rejected'
}


class WXDialogSizer(wx.PySizer):
    """ A custom wx Sizer for use in the WXDialog. This sizers expands
    its child to fit the allowable space, regardless of the settings on
    the child settings. This is similar to how central widgets behave 
    in a WXWindow. 

    There can only be one widget in this sizer at a time and it should
    be added via the .Add(...) method. Old items will be removed 
    automatically (but not destroyed).

    """
    def __init__(self, *args, **kwargs):
        super(WXDialogSizer, self).__init__(*args, **kwargs)
        self._widget = None

    def Add(self, widget):
        """ Adds the given widget to the sizer, removing the old widget
        if present. The old widget is not destroyed.

        """
        self.Clear(deleteWindows=False)
        self._widget = widget
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
        widget = self._widget
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

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def accept(self):
        """ Close the dialog and set the result to 'accepted'.

        """
        self.widget.EndModal(wx.ID_OK)

    def reject(self):
        """ Close the dialog and set the result to 'rejected'.

        """
        self.widget.EndModal(wx.ID_CANCEL)

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

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
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
            retcode = widget.ShowModal()
        else:
            retcode = wx.ID_CANCEL
        self._handle_retcode(retcode)
    
    #--------------------------------------------------------------------------
    # Auxiliary Methods 
    #--------------------------------------------------------------------------
    def _handle_retcode(self, retcode):
        """ Destroys the dialog, fires events, and set status attributes.

        """
        shell = self.shell_obj
        result = DIALOG_RETCODE_MAP[retcode]
        shell._result = result
        shell._active = False
        shell.closed(result)
        # Explicitly Destroy the dialog or the wxApp won't properly exit.
        # We can't simply destroy the shell object since the user may
        # still need something from it.
        widget = self.widget
        if widget:
            widget.Destroy()        

