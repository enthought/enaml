#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui

from traits.api import implements

from .qt_component import QtComponent

from ..panel import IPanelImpl


class QtPanel(QtComponent):
    """ A Qt implementation of Panel.

    A panel arranges its children onto a QFrame.

    See Also
    --------
    Panel

    """
    implements(IPanelImpl)

    #---------------------------------------------------------------------------
    # IPanelImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying QFrame.

        """
        self.widget = QtGui.QFrame(self.parent_widget())
    
    def initialize_widget(self):
        """ There is nothing to initialize on a panel.

        """
        pass

    def create_style_handler(self):
        """ Creates and sets the window style handler.

        """
        pass
    
    def initialize_style(self):
        """ Initializes the style for the window.

        """
        pass
    
    def layout_child_widgets(self):
        """ Arrange the child widgets onto the panel. The children are
        all Containers which provide their own layout. Typically, there
        will be only one container, but in case there are more, all 
        containers get added to a vertical box sizer.

        """
        layout = QtGui.QVBoxLayout()
        for child in self.child_widgets():
            if isinstance(child, QtGui.QLayout):
                layout.addLayout(child)
            else:
                layout.addWidget(child)
        self.widget.setLayout(layout)
