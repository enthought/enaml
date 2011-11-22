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
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        self.widget = wx.Dialog(self.parent_widget(), style=style)
        self._frame = self.widget

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
    def set_visible(self, visible):
        """ Overridden from the parent class to properly launch and close 
        the dialog.

        """
        if not self._initializing:
            widget = self.widget
            shell = self.shell_obj
            if visible:
                shell.trait_set(_active=True, opened=True)
                # Wx doesn't reliably emit resize events when making a 
                # ui visible. So this extra call to update cns helps make 
                # sure things are arranged nicely.
                self.shell_obj.set_needs_update_constraints()
                # wx cannot distinguish between app modal and 
                # window modal, so we only get one kind.
                widget.ShowModal()
            else:
                self.reject()
    
    #--------------------------------------------------------------------------
    # Helper Methods 
    #--------------------------------------------------------------------------
    def _close_dialog(self, result):
        """ Destroy the dialog, fire events, and set status attributes.

        """
        # Explicitly Destroy the dialog or the wxApp won't properly exit.
        if self.widget:
            self.widget.Destroy()
        self.shell_obj.trait_set(_result=result, _active=False, closed=result)

