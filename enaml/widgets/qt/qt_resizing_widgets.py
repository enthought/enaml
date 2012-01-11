#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
""" Subclasses of standard QWidgets that add a `resized` signal that will pass
on notifications of resize events to Enaml.

"""

from abc import ABCMeta

from .qt import QtCore, QtGui, qt_api


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


# For the mixins, we will use a different base class for PySide than for PyQt4.
if qt_api.lower() == 'pyside':
    MixinBaseClass = object
else:
    MixinBaseClass = QtGui.QWidget


class ResizingMixin(MixinBaseClass):
    """ Add a `resized` signal to the widget and a `resizeEvent()` method that
    emits the signal.

    Note: Under PySide 1.0.8, the base class of this mixin must be `object`
    while under PyQt4, it must be `QWidget`.

    """


    resized = QtCore.Signal()

    def resizeEvent(self, event):
        super(ResizingMixin, self).resizeEvent(event)
        self.resized.emit()


class LayoutDebugMixin(MixinBaseClass):
    """ A mixin that can be added to a container widget to draw the positions of
    its children.

    """

    def paintEvent(self, event):
        super(LayoutDebugMixin, self).paintEvent(event)
        qp = QtGui.QPainter()
        qp.begin(self)
        try:
            qp.setPen(QtGui.QColor(0, 0, 0))
            for child in self.children():
                layout_item = QtGui.QWidgetItem(child)
                geom = layout_item.geometry()
                qp.drawRect(geom)
        finally:
            qp.end()


class QResizingFrame(ResizingMixin, QtGui.QFrame):
    """ A QFrame subclass that passes its resize events back to Enaml through
    a Qt signal.

    """

class QResizingDialog(ResizingMixin, QtGui.QDialog):
    """ A QDialog subclass that passes its resize events back to Enaml through
    a Qt signal.

    """


class QResizingGroupBox(ResizingMixin, QtGui.QGroupBox):
    """ A QGroupBox subclass that passes its resize events back to Enaml through
    a Qt signal.

    """


class QResizingStackedWidget(ResizingMixin, QtGui.QStackedWidget):
    """ A QStackedWidget subclass that passes its resize events back to Enaml through
    a Qt signal.

    """


class QResizingScrollArea(ResizingMixin, QtGui.QScrollArea):
    """ A QScrollArea subclass that passes its resize events back to Enaml through
    a Qt signal.

    """


class QResizingTabWidget(ResizingMixin, QtGui.QTabWidget):
    """ A QTabWidget subclass that passes its resize events back to Enaml 
    through a Qt signal.

    """


class QResizingSplitter(ResizingMixin, QtGui.QSplitter):
    """ A QSplitter subclass that passes its resize events back to Enaml through
    a Qt signal.

    """

