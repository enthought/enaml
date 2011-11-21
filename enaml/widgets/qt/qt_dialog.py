#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore
from .qt_window import QtWindow
from .qt_resizing_widgets import QResizingDialog

from ..dialog import AbstractTkDialog


_MODAL_MAP = {
    'application_modal': QtCore.Qt.ApplicationModal,
    'window_modal': QtCore.Qt.WindowModal,
}


class QtDialog(QtWindow, AbstractTkDialog):
    """ A Qt implementation of a Dialog.

    This class creates a simple top-level dialog.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QDialog control.

        """
        self.widget = QResizingDialog(self.parent_widget())

    def initialize(self):
        """ Intializes the attributes on the QDialog.

        """
        super(QtDialog, self).initialize()
        self.widget.finished.connect(self._on_close)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def accept(self):
        """ Accept and close the dialog, sending the 'finished' signal.

        """
        self.widget.accept()

    def reject(self):
        """ Reject and close the dialog, sending the 'finished' signal.

        """
        self.widget.reject()

    #--------------------------------------------------------------------------
    # Event Handlers 
    #--------------------------------------------------------------------------
    def _on_close(self, qt_result):
        """ The event handler for the dialog's finished signal. 

        This translates from a QDialog result into an Enaml result enum
        value. The default result is rejection.

        """
        if qt_result == QtGui.QDialog.Accepted:
            result = 'accepted'
        else:
            result = 'rejected'
        self.shell_obj.trait_set(_result=result, _active=False, closed=result)

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
                widget.setWindowModality(_MODAL_MAP[shell.modality])
                widget.exec_()
            else:
                self.reject()

