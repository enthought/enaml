#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
""" Subclasses of standard QWidgets that add a `resized` signal that will pass
on notifications of resize events to Enaml.

"""

from abc import ABCMeta

from .qt import QtCore, QtGui


class QResizingWidget(object):
    """ An abstract base class for testing if a QWidget subclass exposes
    a `resized` signal.

    """
    __metaclass__ = ABCMeta

    @classmethod
    def __subclasshook__(cls, C):
        """ Check if a class is a QWidget that has the `resized` signal.

        """
        if issubclass(C, QtGui.QWidget):
            if any(isinstance(getattr(B, "resized", None), QtCore.Signal) for B in C.__mro__):
                return True
        return NotImplemented

# It would be cleaner to have a mixin, but this causes segfaults with PySide
# 1.0.8, and simply may never work. The way that the wrappers add signals
# defined on the Python side to the C++ classes may not work with multiple
# inheritance. Consequently, we have to duplicate code.

class QResizingFrame(QtGui.QFrame):
    """ A QFrame subclass that passes its resize events back to Enaml through
    a Qt signal.

    """

    resized = QtCore.Signal()

    def resizeEvent(self, event):
        super(QResizingFrame, self).resizeEvent(event)
        self.resized.emit()


class QResizingDialog(QtGui.QDialog):
    """ A QDialog subclass that passes its resize events back to Enaml through
    a Qt signal.

    """

    resized = QtCore.Signal()

    def resizeEvent(self, event):
        super(QResizingDialog, self).resizeEvent(event)
        self.resized.emit()


class QResizingGroupBox(QtGui.QGroupBox):
    """ A QGroupBox subclass that passes its resize events back to Enaml through
    a Qt signal.

    """

    resized = QtCore.Signal()

    def resizeEvent(self, event):
        super(QResizingGroupBox, self).resizeEvent(event)
        self.resized.emit()


class QResizingStackedWidget(QtGui.QStackedWidget):
    """ A QStackedWidget subclass that passes its resize events back to Enaml through
    a Qt signal.

    """

    resized = QtCore.Signal()

    def resizeEvent(self, event):
        super(QResizingStackedWidget, self).resizeEvent(event)
        self.resized.emit()


class QResizingScrollArea(QtGui.QScrollArea):
    """ A QScrollArea subclass that passes its resize events back to Enaml through
    a Qt signal.

    """

    resized = QtCore.Signal()

    def resizeEvent(self, event):
        super(QResizingScrollArea, self).resizeEvent(event)
        self.resized.emit()
