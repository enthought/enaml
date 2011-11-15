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
        # The parent WXWindow class expects there to be a _frame 
        # attribute available.
        self.widget = self._frame = wx.Dialog(self.parent_widget())

    def initialize(self):
        """ Intializes the attributes on the wx.Dialog.

        """
        super(WXDialog, self).initialize()
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
            shell = self.shell_obj
            shell.trait_set(
                _active = True,
                opened = True,
            )
            # wx cannot distinguish between app modal and 
            # window modal, so we only get one kind.
            widget.ShowModal()

    def hide(self):
        """ Overridden parent class method. Hiding a dialog is the same
        as rejecting it.

        """
        widget = self.widget
        if widget and widget.IsShown():
            self.reject()

    def accept(self):
        """ Close the dialog and set the result to 'accepted'.

        """
        self._close_dialog('accepted')

    def reject(self):
        """ Close the dialog and set the result to 'rejected'.

        """
        self._close_dialog('rejected')

    def _close_dialog(self, result):
        """ Destroy the dialog, fire events, and set status attributes.

        """
        if self.widget:
            self.widget.Destroy()
        self.shell_obj.trait_set(
            _result = result, 
            _active = False,
            closed = result,
        )

    #---------------------------------------------------------------------------
    # Event handling
    #---------------------------------------------------------------------------
    def _on_close(self, event):
        """ Destroy the dialog to handle the EVT_CLOSE event. This will 
        happen if the user clicks on the 'X'. This is equivalent to
        calling 'reject()'.

        """
        self.reject()

