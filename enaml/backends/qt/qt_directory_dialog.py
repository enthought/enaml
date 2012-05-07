#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os

from .qt.QtGui import QFileDialog
from .qt_dialog import QtDialog

from ...components.directory_dialog import AbstractTkDirectoryDialog
from ...guard import guard


class QtDirectoryDialog(QtDialog, AbstractTkDirectoryDialog):
    """ A Qt4 implementation of a DirectoryDialog.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QFileDialog control.

        """
        self.widget = QFileDialog(parent)

    def initialize(self):
        """ Initializes the attributes of the underlying QFileDialog.

        """
        super(QtDirectoryDialog, self).initialize()
        shell = self.shell_obj
        self.set_directory(shell.directory)
        self.widget.setAcceptMode(QFileDialog.AcceptOpen)
        self.widget.setFileMode(QFileDialog.DirectoryOnly)
        self.widget.setViewMode(QFileDialog.Detail)

    def bind(self):
        """ Binds the signal handlers for the file dialog.

        """
        super(QtDirectoryDialog, self).bind()
        widget = self.widget
        widget.filesSelected.connect(self.on_files_selected)

    #--------------------------------------------------------------------------
    # Shell Object Change Handlers
    #--------------------------------------------------------------------------
    def shell_directory_changed(self, directory):
        """ Update the dialog with the new working directory.

        """
        if not guard.guarded(self, 'setting_directory'):
            self.set_directory(directory)
                
    #--------------------------------------------------------------------------
    # Event Handlers 
    #--------------------------------------------------------------------------
    def on_files_selected(self, files):
        """ The signal handler for the dialog's `filesSelected` signal.

        """
        shell = self.shell_obj
        first_file = files[0] if files else u''
        with guard(self, 'setting_directory'):
            shell.directory = first_file

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_directory(self, directory):
        """ Sets the current directory of the dialog.

        """
        self.widget.setDirectory(directory)

    def set_central_widget(self, widget):
        """ Overridden parent class method which makes central widget
        operations a no-op, since a file dialog has no children.

        """
        pass

