#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

from .qt import QtCore
from .qt_layout_component import QtLayoutComponent
from .qt_resizing_widgets import QResizingFrame, QResizingWidget

from ..container import AbstractTkContainer


class _QResizingFrame(QResizingFrame):
    """ A subclass of QResizingFrame which calls back onto the shell
    Container to get the size hint. If that size hint is invalid, it
    falls back onto the Qt default.

    """
    def __init__(self, qt_container, *args, **kwargs):
        super(QResizingFrame, self).__init__(*args, **kwargs)
        self.qt_container = weakref.ref(qt_container)
    
    def sizeHint(self):
        """ Computes the size hint from the given Container, falling
        back on the default size hint computation if the Container 
        returns one that is invalid.

        """
        res = None
        qt_container = self.qt_container()
        if qt_container is not None:
            shell = qt_container.shell_obj
            if shell is not None:
                sh = shell.size_hint()
                if sh != (-1, -1):
                    res = QtCore.QSize(*sh)
        if res is None:
            res = super(_QResizingFrame, self).sizeHint()
        return res


class QtContainer(QtLayoutComponent, AbstractTkContainer):
    """ A Qt4 implementation of Container.

    """
    def create(self, parent):
        """ Creates the underlying Qt widget.

        """
        self.widget = _QResizingFrame(self, parent)

    def bind(self):
        """ Binds the signal handlers for the widget.

        """
        super(QtContainer, self).bind()
        widget = self.widget
        if isinstance(widget, QResizingWidget):
            widget.resized.connect(self.on_resize)

    def on_resize(self):
        """ Triggers a relayout of the shell object since the widget
        has been resized.

        """
        # Notice that we are calling refresh() here instead of 
        # request_refresh() since we want the refresh to happen
        # immediately. Otherwise the resize layouts will appear 
        # to lag in the ui. This is a safe operation since by the
        # time we get this resize event, the widget has already 
        # changed size. Further, the only geometry that gets set
        # by the layout manager is that of our children. And should
        # it be required to resize this widget from within the layout
        # call, then the layout manager will do that asynchronously.
        self.shell_obj.refresh()

