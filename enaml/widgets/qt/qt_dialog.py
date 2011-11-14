#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_window import QtWindow
from .qt_resizing_widgets import QResizingDialog

from ..dialog import AbstractTkDialog


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
        """ Displays this dialog to the screen.

        If the dialog is modal, disable all other windows in the application.

        """
        widget = self.widget
        if widget:
            shell = self.shell_obj
            shell.trait_set(
                _active = True,
                opened = True,
            )
            if shell.modality in ('application_modal', 'window_modal'):
                widget.exec_()
            else:
                widget.show()

    def open(self):
        """ Display the dialog.

        """
        self.show()

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

