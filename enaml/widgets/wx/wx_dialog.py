#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from traits.api import implements

from .wx_window import WXWindow

from ..dialog import IDialogImpl

from ...enums import DialogResult


class WXDialog(WXWindow):
    """ A wxPython implementation of a Dialog.

    WXDialog uses a wx.Dialog to create a simple top-level dialog.

    See Also
    --------
    Dialog

    """
    implements(IDialogImpl)

    #---------------------------------------------------------------------------
    # IDialogImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying wx.Dialog control.

        """
        self.widget = wx.Dialog(self.parent_widget())

    def initialize_widget(self):
        """ Intializes the attributes on the wx.Dialog.
        
        """
        super(WXDialog, self).initialize_widget()
        self.widget.Bind(wx.EVT_CLOSE, self._on_close)

    def show(self):
        """ Displays this dialog to the screen.
        
        If the dialog is modal, disable all other windows in the application.
        
        """
        widget = self.widget
        if widget:
            if widget.IsModal():
                widget.ShowModal()
            else:
                widget.Show()
            self.parent._active = True

    def open(self):
        """ Display the dialog.
        
        """
        self.show()

    def accept(self):
        """ Close the dialog and set the result to DialogResult.ACCEPTED.
        
        """
        self.parent._result = DialogResult.ACCEPTED
        self.close_dialog()
    
    def reject(self):
        """ Close the dialog and set the result to DialogResult.REJECTED.
        
        """
        self.parent._result = DialogResult.REJECTED
        self.close_dialog()

    #---------------------------------------------------------------------------
    # Event handling
    #---------------------------------------------------------------------------
    def _on_close(self, event):
        """ Destroy the dialog to handle the EVT_CLOSE event.
        
        """
        self.close_dialog()
        event.Skip()
    
    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def close_dialog(self):
        """ Destroy the dialog, fire events, and set status attributes.
        
        """
        self.widget.Destroy()
        parent = self.parent
        parent.closed = parent.result
        parent._active = False
                
