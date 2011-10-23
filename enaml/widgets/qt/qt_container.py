#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import implements

from .qt import QtGui, QtCore
from .qt_component import QtComponent
from .qt_layout_item import QtLayoutItem
from ..container import IContainerImpl


class QResizingFrame(QtGui.QFrame):

    resized = QtCore.Signal()

    def resizeEvent(self, event):
        self.resized.emit()


class QtContainer(QtComponent, QtLayoutItem):
    """ A Qt implementation of Container.

    The QtContainer class serves as a base class for other container
    widgets. It is not meant to be used directly.

    See Also
    --------
    Container

    """
    implements(IContainerImpl)

    #---------------------------------------------------------------------------
    # IContainerImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates and sets the window style handler.

        """
        self.widget = QResizingFrame(self.parent_widget())
    
    def initialize_widget(self):
        pass

    def initialize_layout(self):
        self.widget.resized.connect(self.on_resize)

    def on_resize(self):
        self.parent.relayout()

