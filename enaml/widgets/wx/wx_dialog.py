#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx


from .wx_window import WXWindow

from ..dialog import AbstractTkDialog


class WXDialog(WXWindow, AbstractTkDialog):
    """ A wxPython implementation of a Dialog.

    WXDialog uses a wx.Dialog to create a simple top-level dialog.

    """

    #---------------------------------------------------------------------------
    # Setup methods
    #---------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying wx.Dialog control.

        """
        self.widget = wx.Dialog(self.parent_widget())

    def initialize(self):
        """ Intializes the attributes on the wx.Dialog.

        """
        super(WXDialog, self).initialize_widget()
        self.widget.Bind(wx.EVT_CLOSE, self._on_close)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------

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
            self.shell_obj._active = True

    def open(self):
        """ Display the dialog.

        """
        self.show()

    def accept(self):
        """ Close the dialog and set the result to 'accepted'.

        """
        self.shell_obj._result = 'accepted'
        self.close_dialog()

    def reject(self):
        """ Close the dialog and set the result to 'rejected'.

        """
        self.shell_obj._result = 'rejected'
        self.close_dialog()

    def close_dialog(self):
        """ Destroy the dialog, fire events, and set status attributes.

        """
        self.widget.Destroy()
        shell = self.shell_obj
        shell.trait_set(
            closed = shell.result,
            _active = False,
        )

    #---------------------------------------------------------------------------
    # Event handling
    #---------------------------------------------------------------------------
    def _on_close(self, event):
        """ Destroy the dialog to handle the EVT_CLOSE event.

        """
        self.close_dialog()
        event.Skip()

