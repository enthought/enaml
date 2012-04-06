#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore
from .qt_window import QtWindow, QtWindowLayout
from .qt_resizing_widgets import QResizingDialog

from ...components.dialog import AbstractTkDialog


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
    def create(self, parent):
        """ Creates the underlying QDialog control.

        """
        self.widget = QResizingDialog(parent)
        self.widget.setLayout(QtWindowLayout())

    def bind(self):
        """ Bind the signal handlers for the dialog.

        """
        super(QtDialog, self).initialize()
        self.widget.finished.connect(self._on_close)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
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
        shell = self.shell_obj
        shell._result = result
        shell._active = False
        shell.closed(result)

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ Overridden from the parent class to properly launch and close 
        the dialog with the specified modality.

        """
        widget = self.widget
        shell = self.shell_obj
        if visible:
            shell._active = True
            shell.opened()
            widget.setWindowModality(_MODAL_MAP[shell.modality])
            widget.exec_()
        else:
            self.reject()

