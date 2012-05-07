#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os

import wx

from .wx_dialog import WXDialog

from ...components.directory_dialog import AbstractTkDirectoryDialog
from ...guard import guard


class WXDirectoryDialog(WXDialog, AbstractTkDirectoryDialog):
    """ A Wx implementation of a DirectoryDialog.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.DirDialog control.

        """
        self.widget = wx.DirDialog(parent)

    def initialize(self):
        """ Initializes the attributes of the underlying wx.DirDialog.

        """
        super(WXDirectoryDialog, self).initialize()
        shell = self.shell_obj
        self.set_directory(shell.directory)
    
    # The wx.DirDialog doesn't emit events for anything useful, 
    # so there is nothing which need be bound.

    #--------------------------------------------------------------------------
    # Shell Object Change Handlers
    #--------------------------------------------------------------------------
    def shell_directory_changed(self, directory):
        """ Update the dialog with the new working directory.

        """
        if not guard.guarded(self, 'setting_directory'):
            self.set_directory(directory)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_directory(self, directory):
        """ Sets the current directory of the dialog.

        """
        self.widget.SetPath(directory)

    def set_central_widget(self, widget):
        """ Overridden parent class method which makes central widget
        operations a no-op, since a directory dialog has no children.

        """
        pass

    #--------------------------------------------------------------------------
    # Auxiliary Methods 
    #--------------------------------------------------------------------------
    def _handle_retcode(self, retcode):
        """ Overridden parent class method to update the shell object
        with new info once the dialog is closed.

        """
        widget = self.widget
        shell = self.shell_obj
        if retcode == wx.ID_OK:
            path = widget.GetPath()
            with guard(self, 'setting_directory'):
                shell.directory = path
        super(WXDirectoryDialog, self)._handle_retcode(retcode)

