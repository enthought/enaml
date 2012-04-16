#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from os.path import split
import wx

from .wx_dialog import WXDialog, WXDialogSizer

from ...components.file_dialog import FileDialog


class WXFileDialog(WXDialog):
    """ A WX implementation of a FileDialog.
    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.FileDialog control.

        """
        shell = self.shell_obj
        
        # If the caller provided a default path instead of a default directory
        # and filename, split the path into it directory and filename
        # components.
        if len(shell.default_path) != 0 and len(shell.default_directory) == 0 \
            and len(shell.default_filename) == 0:
            default_directory, default_filename = \
                os.path.split(shell.default_path)
        else:
            default_directory = shell.default_directory
            default_filename = shell.default_filename

        if shell.type == 'open':
            style = wx.OPEN
        elif shell.type == 'open files':
            style = wx.OPEN | wx.MULTIPLE
        else:
            style = wx.SAVE | wx.OVERWRITE_PROMPT

        # Create the actual dialog.
        widget = wx.FileDialog(parent, shell.title,
                    defaultDir=default_directory,
                    defaultFile=default_filename, style=style,
                    wildcard=shell.wildcard.rstrip('|'))
        widget.SetFilterIndex(shell.wildcard_index)
        widget.SetSizer(WXDialogSizer())

        self.widget = widget

    #--------------------------------------------------------------------------
    # Auxiliary Methods 
    #--------------------------------------------------------------------------
    def _close_dialog(self, result):
        """ The event handler for the dialog's finished signal.
        """
        widget = self.widget
        shell = self.shell_obj

        # Get the path of the chosen directory.
        shell.path = unicode(widget.GetPath())
        
        # Work around wx bug throwing exception on cancel of file dialog
        if len(shell.path) > 0:
            shell.paths = widget.GetPaths()
        else:
            shell.paths = [u'']

        # Extract the directory and filename.
        shell.directory, shell.filename = os.path.split(shell.path)

        # Get the index of the selected filter.
        shell.wildcard_index = widget.GetFilterIndex()

        # Fire off the appropriate event
        if result == 'accepted':
            shell.accepted()
        else:
            shell.rejected()

        # Let the dialog close as normal.
        super(WXFileDialog, self)._close_dialog(result)


