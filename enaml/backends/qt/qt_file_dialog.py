#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os

from .qt.QtGui import QFileDialog
from .qt_dialog import QtDialog

from ...components.file_dialog import AbstractTkFileDialog
from ...guard import guard


ACCEPT_MODE_MAP = {
    'open': QFileDialog.AcceptOpen,
    'save': QFileDialog.AcceptSave,
}


class QtFileDialog(QtDialog, AbstractTkFileDialog):
    """ A Qt4 implementation of a FileDialog.

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
        super(QtFileDialog, self).initialize()
        shell = self.shell_obj
        self.set_mode(shell.mode)
        self.set_multi_select(shell.multi_select)
        self.set_directory(shell.directory)
        self.set_filename(shell.filename)
        self.set_filters(shell.filters)
        self.set_selected_filter(shell.selected_filter)
        self.widget.setViewMode(QFileDialog.Detail)

    def bind(self):
        """ Binds the signal handlers for the file dialog.

        """
        super(QtFileDialog, self).bind()
        widget = self.widget
        widget.filesSelected.connect(self.on_files_selected)
        widget.filterSelected.connect(self.on_filter_selected)

    #--------------------------------------------------------------------------
    # Shell Object Change Handlers
    #--------------------------------------------------------------------------
    def shell_mode_changed(self, mode):
        """ Update the dialog for the given mode of behavior.

        """
        self.set_mode(mode)

    def shell_multi_select_changed(self, multi_select):
        """ Update the dialog for the given multi select behavior.

        """
        self.set_multi_select(multi_select)

    def shell_directory_changed(self, directory):
        """ Update the dialog with the new working directory.

        """
        if not guard.guarded(self, 'setting_directory'):
            self.set_directory(directory)
                
    def shell_filename_changed(self, filename):
        """ Update the dialog with the new selected filename.

        """
        if not guard.guarded(self, 'setting_filename'):
            self.set_filename(filename)

    def shell_filters_changed(self, filters):
        """ Update the dialog with the new filename filters.

        """
        # Traits doens't fire off a change event if an Enum updates
        # because its underlying values have changed. So, we just 
        # set the selected filter manually here to cover that case.
        self.set_filters(filters)
        self.set_selected_filter(self.shell_obj.selected_filter)

    def shell_selected_filter_changed(self, selected_filter):
        """ Update the dialog with the new selected filter.

        """
        if not guard.guarded(self, 'setting_selected_filter'):
            self.set_selected_filter(selected_filter)

    #--------------------------------------------------------------------------
    # Event Handlers 
    #--------------------------------------------------------------------------
    def on_files_selected(self, files):
        """ The signal handler for the dialog's `filesSelected` signal.

        """
        shell = self.shell_obj
        first_file = files[0] if files else u''
        with guard(self, 'setting_directory'):
            with guard(self, 'setting_filename'):
                shell.directory, shell.filename = os.path.split(first_file)
                shell._paths = files

    def on_filter_selected(self, qt_filter):
        """ The signal handler for the dialog's `filterSelected` signal.

        """
        shell = self.shell_obj
        with guard(self, 'setting_selected_filter'):
            shell.selected_filter = qt_filter

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_mode(self, mode):
        """ Sets the mode behavior of the file dialog.

        """
        self.widget.setAcceptMode(ACCEPT_MODE_MAP[mode])
    
    def set_multi_select(self, multi_select):
        """ Sets the multi select behavior of the file dialog.

        """
        widget = self.widget
        if widget.acceptMode() == QFileDialog.AcceptSave:
            mode = QFileDialog.AnyFile
        else:
            if multi_select:
                mode = QFileDialog.ExistingFile
            else:
                mode = QFileDialog.ExistingFiles
        widget.setFileMode(mode)

    def set_directory(self, directory):
        """ Sets the current directory of the dialog.

        """
        self.widget.setDirectory(directory)
    
    def set_filename(self, filename):
        """ Sets the selected filename in the dialog.

        """
        self.widget.selectFile(filename)
    
    def set_filters(self, filters):
        """ Sets the name filters in the file dialog.

        """
        self.widget.setNameFilters(filters)
    
    def set_selected_filter(self, selected_filter):
        """ Sets the selected name filter in the file dialog.

        """
        self.widget.selectNameFilter(selected_filter)

    def set_central_widget(self, widget):
        """ Overridden parent class method which makes central widget
        operations a no-op, since a file dialog has no children.

        """
        pass

