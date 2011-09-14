from .qt import QtCore, QtGui

from traits.api import implements, Instance

from .qt_component import QtComponent

from ..window import IWindowImpl

from ...enums import Modality


class QtWindow(QtComponent):
    """ A Qt implementation of a Window.

    QtWindow uses a QFrame to create a simple top level window which
    contains other child widgets and layouts.

    See Also
    --------
    Window

    """
    implements(IWindowImpl)

    #---------------------------------------------------------------------------
    # IWindowImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying QWindow control.

        """
        self.widget = QtGui.QFrame(self.parent_widget())
    
    def initialize_widget(self):
        """ Intializes the attributes on the QWindow.

        """
        self.set_title(self.parent.title)
        self.set_modality(self.parent.modality)

    def layout_child_widgets(self):
        """ Arranges the children of the QWindow (typically only one) in
        a vertical box layout.

        """
        layout = QtGui.QVBoxLayout()
        for child in self.child_widgets():
            if isinstance(child, QtGui.QLayout):
                layout.addLayout(child, 1)
            else:
                layout.addWidget(child, 1)
        self.widget.setLayout(layout)

    def show(self):
        """ Displays the window to the screen.
        
        """
        if self.widget:
            self.widget.show()

    def hide(self):
        """ Hide the window from the screen.

        """
        if self.widget:
            self.widget.hide()

    def parent_title_changed(self, title):
        """ The change handler for the 'title' attribute. Not meant for 
        public consumption.

        """
        self.set_title(title)
    
    def parent_modality_changed(self, modality):
        """ The change handler for the 'modality' attribute. Not meant 
        for public consumption.

        """
        self.set_modality(modality)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def set_title(self, title):
        """ Sets the title of the QFrame. Not meant for public 
        consumption.

        """
        if self.widget:
            self.widget.setWindowTitle(title)
    
    def set_modality(self, modality):
        """ Sets the modality of the QMainWindow. Not meant for public
        consumption.

        """
        if self.widget:
            if modality == Modality.APPLICATION_MODAL:
                self.widget.setWindowModality(QtCore.Qt.ApplicationModal)
            elif modality == Modality.WINDOW_MODAL:
                self.widget.setWindowModality(QtCore.Qt.WindowModal)
            else:
                self.widget.setWindowModality(QtCore.Qt.NonModal)

