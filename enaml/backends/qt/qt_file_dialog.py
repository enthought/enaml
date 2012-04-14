#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from os.path import split

from .qt import QtGui, QtCore
from .qt_dialog import QtDialog

from ...components.file_dialog import FileDialog


class QtFileDialog(QtDialog):
    """ A Qt implementation of a FileDialog.
    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QFileDialog control.

        """
        shell = self.shell_obj
        
        # If the caller provided a default path instead of a default directory
        # and filename, split the path into it directory and filename
        # components.
        if len(shell.default_path) != 0 and len(shell.default_directory) == 0 \
            and len(shell.default_filename) == 0:
            default_directory, default_filename = split(shell.default_path)
        else:
            default_directory = shell.default_directory
            default_filename = shell.default_filename

        # Convert the filter.
        filters = []
        for filter_list in shell.wildcard.split('|')[::2]:
            # Qt uses spaces instead of semicolons for extension separators
            filter_list = filter_list.replace(';', ' ')
            filters.append(filter_list)

        # Set the default directory.
        if not default_directory:
            default_directory = QtCore.QDir.currentPath()

        widget = QtGui.QFileDialog(parent, shell.title, default_directory)

        widget.setViewMode(QtGui.QFileDialog.Detail)
        widget.selectFile(default_filename)
        widget.setNameFilters(filters)

        if shell.wildcard_index < len(filters):
            widget.selectNameFilter(filters[shell.wildcard_index])

        if shell.type == 'open':
            widget.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
            widget.setFileMode(QtGui.QFileDialog.ExistingFile)
        else:
            widget.setAcceptMode(QtGui.QFileDialog.AcceptSave)
            widget.setFileMode(QtGui.QFileDialog.AnyFile)

        self.widget = widget


    #--------------------------------------------------------------------------
    # Event Handlers 
    #--------------------------------------------------------------------------
    def _on_close(self, qt_result):
        """ The event handler for the dialog's finished signal.
        """
        widget = self.widget
        shell = self.shell_obj
        
        # Get the path of the chosen directory.
        files = widget.selectedFiles()

        if files:
            shell.path = unicode(files[0])
        else:
            shell.path = ''

        # Extract the directory and filename.
        shell.directory, shell.filename = split(shell.path)

        # Get the index of the selected filter.
        shell.wildcard_index = widget.nameFilters().index(
            widget.selectedNameFilter())

        super(QtFileDialog, self)._on_close(qt_result)


