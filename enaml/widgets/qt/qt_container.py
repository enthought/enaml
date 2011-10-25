#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore
from .qt_component import QtComponent
from .qt_layout_item import QtLayoutItem
from ..container import AbstractTkContainer


class QResizingFrame(QtGui.QFrame):
    """ A QFrame subclass that converts a resize event into a signal
    that can be connected to a slot. This allows the widget to notify
    Enaml that it has been resized and the layout needs to be recomputed.

    """
    resized = QtCore.Signal()

    def resizeEvent(self, event):
        self.resized.emit()


class QtContainer(QtComponent, QtLayoutItem, AbstractTkContainer):
    """ A Qt implementation of Container.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self):
        self.widget = QResizingFrame(self.parent_widget())

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def connect(self):
        super(QtContainer, self).connect()
        self.widget.resized.connect(self.on_resize)

    def on_resize(self):
        self.shell_widget.relayout()

