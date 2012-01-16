#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_layout_component import QtLayoutComponent
from .qt_resizing_widgets import QResizingFrame, QResizingWidget

from ..container import AbstractTkContainer


class QtContainer(QtLayoutComponent, AbstractTkContainer):
    """ A Qt4 implementation of Container.

    """
    def create(self, parent):
        """ Creates the underlying Qt widget.

        """
        self.widget = QResizingFrame(parent)
    
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

