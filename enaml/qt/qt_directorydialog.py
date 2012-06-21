#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from qt_dialog import QtDialog
from .qt.QtGui import QFileDialog

class QtDirectoryDialog(QtDialog):
    """ A dialog that allows the user to select directories

    """
    def create(self, parent):
        """ Create the underlying widget

        """
        self.widget = QFileDialog(parent)
        self.widget.show()

    def initialize(self, init_attrs):
        """ Initialize the attributes of the file dialog so that it only
        accepts directories

        """
        self.set_directory(init_attrs.get('directory'))
        self.widget.setAcceptMode(QFileDialog.AcceptOpen)
        self.widget.setFileMode(QFileDialog.Directory)
        self.widget.setOption(QFileDialog.ShowDirsOnly)
        
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_directory(self, ctxt):
        """ Message handler for set_directory

        """
        directory = ctxt.get('value')
        if directory is not None:
            self.set_directory(directory)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_directory(self, directory):
        """ Set the directory of the file dialog

        """
        self.widget.setDirectory(directory)
