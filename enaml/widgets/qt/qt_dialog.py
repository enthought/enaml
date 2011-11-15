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
    def show(self):
        """ Displays this modal dialog to the screen.

        """
        widget = self.widget
        if widget:
            shell = self.shell_obj
            shell.trait_set(
                _active = True,
                opened = True,
            )
            widget.setWindowModality(_MODAL_MAP[shell.modality])
            widget.exec_()

    def hide(self):
        """ Overridden parent class method. Hiding a dialog is the same
        as rejecting it.

        """
        widget = self.widget
        if widget and widget.visible():
            self.reject()

    def accept(self):
        """ Accept and close the dialog, sending the 'finished' signal.

        """
        self.widget.accept()

    def reject(self):
        """ Reject and close the dialog, sending the 'finished' signal.

        """
        self.widget.reject()

    def _on_close(self, qt_result):
        """ Translate from a QDialog result into an Enaml enum.

        The default result is rejection, in case the dialog is closed without
        a response.

        """
        if qt_result == QtGui.QDialog.Accepted:
            result = 'accepted'
        else:
            result = 'rejected'
        self._close_dialog(result)

    def _close_dialog(self, result):
        """ Destroy the dialog, fire events, and set status attributes.

        """
        self.shell_obj.trait_set(
            _result = result,
            _active = False,
            closed = result,
        )

