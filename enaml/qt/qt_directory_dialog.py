#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os
from qt_dialog import QtDialog
from .qt.QtGui import QFileDialog

class QtDirectoryDialog(QtDialog):
    """ A dialog that allows the user to select directories

    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QFileDialog(self.parent_widget)

    def initialize(self, init_attrs):
        """ Initialize the attributes of the file dialog so that it only
        accepts directories

        """
        super(QtDirectoryDialog, self).initialize(init_attrs)
        self.set_directory(init_attrs.get('directory',
                                          os.path.abspath(os.path.curdir)))
        self.widget.setAcceptMode(QFileDialog.AcceptOpen)
        self.widget.setFileMode(QFileDialog.Directory)
        self.widget.setOption(QFileDialog.ShowDirsOnly)

    def bind(self):
        """ Binds the signal handlers for the file dialog.

        """
        super(QtDirectoryDialog, self).bind()
        self.widget.filesSelected.connect(self.on_files_selected)
        
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_directory(self, ctxt):
        """ Message handler for set_directory

        """
        directory = ctxt.get('directory')
        if directory is not None:
            self.set_directory(directory)

    #--------------------------------------------------------------------------
    # Event Handlers 
    #--------------------------------------------------------------------------
    def on_files_selected(self, files):
        """ The signal handler for the dialog's `filesSelected` signal.

        """
        first_directory = files[0] if files else u''
        self.send({'action':'set_directory', 'directory':first_directory})

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_directory(self, directory):
        """ Set the directory of the file dialog

        """
        self.widget.setDirectory(directory)
