#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
""" Subclasses of standard QWidgets that add a `resized` signal that will 
pass on notifications of resize events to Enaml.

"""
from abc import ABCMeta
import os

from .qt import QtCore, QtGui


#: A private flag which is used at startup time to enable debug painting
#: for the Qt resizable widgets.
_debug = os.environ.get('ENAML_DEBUG_PAINT', False)


class QResizingWidget(object):
    """ An abstract base class for testing if a QWidget subclass exposes
    a `resized` signal. Virtual subclasses must explicitly register 
    themselves with the .register() method.

    """
    __metaclass__ = ABCMeta


def _resizable(cls):
    """ A private class decorator/factory which takes a QWidget subclass 
    and adds code which converts its resize events into a 'resized' 
    signal. If the debug paint environment flag is set, it adds the 
    custom painting code as well.

    Paramters
    ---------
    cls : QWidget subclass
        The QWidget subclass to which resizing functionality is added.
    
    Returns
    -------
    result : QWidget subclass
        A new subclass with the resizing functionality implemented.
    
    """
    if _debug:

        class QResizable(cls):
            """ A QWidget subclass that passes its resize events back 
            to Enaml through a Qt signal.

            """
            #: A signal which is emitted on a resize event.
            resized = QtCore.Signal()

            def resizeEvent(self, event):
                """ Converts a resize event in into a signal.

                """
                super(QResizable, self).resizeEvent(event)
                self.resized.emit()
            
            def paintEvent(self, event):
                """ Paints debug layout rects of all the children during
                a paint event.

                """
                super(QResizable, self).paintEvent(event)
                qp = QtGui.QPainter()
                qp.begin(self)
                try:
                    qp.setPen(QtGui.QColor(255, 0, 0))
                    for child in self.children():
                        if isinstance(child, QtGui.QWidget):
                            layout_item = QtGui.QWidgetItem(child)
                            geom = layout_item.geometry()
                            qp.drawRect(geom)
                finally:
                    qp.end()
            
        QResizable.__name__ = cls.__name__ + '_debug_resizable'
                
    else:
        
        class QResizable(cls):
            """ A QWidget subclass that passes its resize events back 
            to Enaml through a Qt signal.

            """
            #: A signal which is emitted on a resize event.
            resized = QtCore.Signal()

            def resizeEvent(self, event):
                """ Converts a resize event in into a signal.

                """
                super(QResizable, self).resizeEvent(event)
                self.resized.emit()
    
        QResizable.__name__ = cls.__name__ + '_resizable' 
          
    QResizingWidget.register(QResizable)

    return QResizable


QResizingFrame = _resizable(QtGui.QFrame)


QResizingDialog = _resizable(QtGui.QDialog)


QResizingMainWindow = _resizable(QtGui.QMainWindow)


QResizingGroupBox = _resizable(QtGui.QGroupBox)


QResizingScrollArea = _resizable(QtGui.QScrollArea)


QResizingTabWidget = _resizable(QtGui.QTabWidget)


QResizingSplitter = _resizable(QtGui.QSplitter)


