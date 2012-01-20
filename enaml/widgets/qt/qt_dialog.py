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


class QtDialogLayout(QtGui.QLayout):
    """ A QLayout subclass which can have at most one layout item. This
    layout item is expanded to fit the allowable space, regardless of its
    size policy settings. This is similar to how central widgets behave 
    in a QMainWindow.

    The class is designed for use by QtDialog, other uses are at the 
    user's own risk.

    """
    def __init__(self, *args, **kwargs):
        super(QtDialogLayout, self).__init__(*args, **kwargs)
        self._layout_item = None
    
    def addItem(self, item):
        """ A virtual method implementation which sets the layout item
        in the layout. Any old item will be overridden.

        """
        self._layout_item = item
        self.update()

    def count(self):
        """ A virtual method implementation which returns 0 if no layout
        item is supplied, or 1 if there is a current layout item.

        """
        return 0 if self._layout_item is None else 1

    def itemAt(self, idx):
        """ A virtual method implementation which returns the layout item 
        for the given index or None if one does not exist.

        """
        if idx == 0:
            return self._layout_item

    def takeAt(self, idx):
        """ A virtual method implementation which removes and returns the
        item at the given index or None if one does not exist.

        """
        if idx == 0:
            res = self._layout_item
            self._layout_item = None
            return res
    
    def sizeHint(self):
        """ A reimplemented method to return a proper size hint for the
        layout, and hence the Dialog.

        """
        return QtCore.QSize(600, 100)

    def setGeometry(self, rect):
        """ A reimplemented method which sets the geometry of the managed
        widget to fill the given rect.

        """
        super(QtDialogLayout, self).setGeometry(rect)
        item = self._layout_item
        if item is not None:
            item.widget().setGeometry(rect)


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
        self.widget.setLayout(QtDialogLayout())

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
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def update_central_widget(self):
        """ Updates the central widget in the dialog with the value from
        the shell object.

        """
        # It's possible for the central widget component to be None.
        # This must be allowed since the central widget may be generated
        # by an Include component, in which case it will not exist 
        # during initialization. However, we must have a central widget
        # for the Dialog, and so we just fill it with a dummy widget.
        central_widget = self.shell_obj.central_widget
        if central_widget is None:
            child_widget = QtGui.QWidget()
        else:
            child_widget = central_widget.toolkit_widget
        self.widget.layout().addWidget(child_widget)

    def set_visible(self, visible):
        """ Overridden from the parent class to properly launch and close 
        the dialog.

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

