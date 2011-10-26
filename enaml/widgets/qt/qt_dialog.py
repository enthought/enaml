#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui

from traits.api import implements

from .qt_window import QtWindow

from ..dialog import IDialogImpl

from ...enums import DialogResult

# XXX punting on dialog for now

class QtDialog(QtWindow):
    """ A Qt implementation of a Dialog.

    This class creates a simple top-level dialog.

    See Also
    --------
    Dialog

    """
    implements(IDialogImpl)

    #--------------------------------------------------------------------------
    # IDialogImpl interface
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying QDialog control.

        """
        self.widget = QtGui.QDialog(self.parent_widget())

    def initialize_widget(self):
        """ Intializes the attributes on the QDialog.
        
        """
        super(QtDialog, self).initialize_widget()
        self.widget.finished.connect(self._on_close)

    def show(self):
        """ Displays this dialog to the screen.
        
        If the dialog is modal, disable all other windows in the application.
        
        """
        widget = self.widget
        if widget:
            widget.show()
            parent = self.parent
            parent._active = True
            parent.opened = True

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
        
    
    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def _on_close(self, qt_result):
        """ Translate from a QDialog result into an Enaml enum.
        
        The default result is rejection, in case the dialog is closed without
        a response.
        
        """
        if qt_result == QtGui.QDialog.Accepted:
            result = DialogResult.ACCEPTED
        else:
            result = DialogResult.REJECTED
        self._close_dialog(result)
        
    def _close_dialog(self, result):
        """ Destroy the dialog, fire events, and set status attributes.
        
        """
        parent = self.parent
        parent._result = result
        parent._active = False
        parent.closed = result
        
