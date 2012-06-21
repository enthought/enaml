#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from PySide.QtGui import QFileDialog
from qt_dialog import QtDialog

QT_ACCEPT_MODE = {
    'open' : QFileDialog.AcceptOpen,
    'save' : QFileDialog.AcceptSave
}

class QtFileDialog(QtDialog):
    """ A Qt implementation of a file dialog

    """
    def create(self, parent):
        """ Create the underlying widget

        """
        self.widget = QFileDialog(parent)
        self.widget.show()

    def initialize(self, init_attrs):
        """ Initialize the attributes of the file dialog

        """
        self.set_mode(init_attrs.get('mode'))
        self.set_multi_select(init_attrs.get('multi_select'))
        self.set_directory(init_attrs.get('directory'))
        self.set_filename(init_attrs.get('filename'))
        self.set_selected_filter(init_attrs.get('selected_filter'))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_mode(self, ctxt):
        """ Message handler for set_mode

        """
        mode = ctxt.get('mode')
        if mode is not None:
            self.set_mode(mode)

    def receive_set_multi_select(self, ctxt):
        """ Message handler for set_multi_select

        """
        multi_select = ctxt.get('multi_select')
        if multi_select is not None:
            self.set_multi_select(multi_select)

    def receive_set_directory(self, ctxt):
        """ Message handler for set_directory

        """
        directory = ctxt.get('directory')
        if directory is not None:
            self.set_directory(directory)

    def receive_set_filename(self, ctxt):
        """ Message handler for set_filename

        """
        filename = ctxt.get('filename')
        if filename is not None:
            self.set_filename(filename)

    def receive_set_filters(self, ctxt):
        """ Message handler for set_filters

        """
        filters = ctxt.get('filters')
        if filters is not None:
            self.set_filters(filters)

    def receive_set_selected_filter(self, ctxt):
        """ Message handler for set_selected_filter

        """
        selected_filter = ctxt.get('selected_filter')
        if selected_filter is not None:
            self.set_selected_filter(selected_filter)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_mode(self, mode):
        """ Set the mode of the file dialog

        """
        self.widget.setAcceptMode(QT_ACCEPT_MODE[mode])

    def set_multi_select(self, multi_select):
        """ Set whether the user can select multiple files when in open mode

        """
        if self.widget.acceptMode() == QFileDialog.AcceptSave:
            mode = QFileDialog.AnyFile
        else:
            if multi_select:
                mode = QFileDialog.ExistingFiles
            else:
                mode = QFileDialog.ExistingFile
        self.widget.setFileMode(mode)

    def set_directory(self, directory):
        """ Set the current directory of the file dialog

        """
        self.widget.setDirectory(directory)

    def set_filename(self, filename):
        """ Set the current filename of the file dialog

        """
        self.widget.setFilename(filename)

    def set_filters(self, filters):
        """ Set the list of name filters for the file dialog

        """
        self.widget.setNameFilters(filters)

    def set_selected_filter(self, selected_filter):
        """ Set the selected filter of the file dialog

        """
        self.widget.selectNameFilter(selected_filter)
