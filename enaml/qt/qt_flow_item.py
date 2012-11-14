#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QFrame
from .q_single_widget_layout import QSingleWidgetLayout
from .qt_container import QtContainer
from .qt_widget_component import QtWidgetComponent


class QFlowItem(QFrame):
    """ A QFrame subclass which acts as an item in a QFlowArea.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a QFlowItem.

        Parameters
        ----------
        *args, **kwargs
            The position and keyword arguments required to initialize
            a QFrame.

        """
        super(QFlowItem, self).__init__(*args, **kwargs)
        self._flow_widget = None
        self.setLayout(QSingleWidgetLayout())

    def flowWidget(self):
        """ Get the flow widget for this flow item.

        Returns
        -------
        result : QWidget or None
            The flow widget being managed by this item.

        """
        return self._flow_widget

    def setFlowWidget(self, widget):
        """ Set the flow widget for this flow item.

        Parameters
        ----------
        widget : QWidget
            The QWidget to use as the flow widget in this item.

        """
        self._flow_widget = widget
        self.layout().setWidget(widget)


class QtFlowItem(QtWidgetComponent):
    """ A Qt implementation of an Enaml FlowItem.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QFlowItem widget.

        """
        return QFlowItem(parent)

    def init_layout(self):
        """ Initialize the layout for the underyling widget.

        """
        super(QtFlowItem, self).init_layout()
        self.widget().setFlowWidget(self.flow_widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def flow_widget(self):
        """ Find and return the flow widget child for this widget.

        Returns
        -------
        result : QWidget or None
            The flow widget defined for this widget, or None if one is
            not defined.

        """
        widget = None
        for child in self.children():
            if isinstance(child, QtContainer):
                widget = child.widget()
        return widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child added event for a QtFlowItem.

        """
        if isinstance(child, QtContainer):
            self.widget().setFlowWidget(self.flow_widget())

    def child_added(self, child):
        """ Handle the child added event for a QtFlowItem.

        """
        if isinstance(child, QtContainer):
            self.widget().setFlowWidget(self.flow_widget())

