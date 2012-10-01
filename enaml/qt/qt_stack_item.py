#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QWidget
from .q_single_widget_layout import QSingleWidgetLayout
from .qt_container import QtContainer
from .qt_widget_component import QtWidgetComponent


class QStackItem(QWidget):
    """ A QWidget subclass which acts as an item QStack.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a QStackItem.

        Parameters
        ----------
        *args, **kwargs
            The position and keyword arguments required to initialize
            a QWidget.

        """
        super(QStackItem, self).__init__(*args, **kwargs)
        self._stack_widget = None
        self.setLayout(QSingleWidgetLayout())

    def stackWidget(self):
        """ Get the stack widget for this stack item.

        Returns
        -------
        result : QWidget or None
            The stack widget being managed by this item.

        """
        return self._stack_widget

    def setStackWidget(self, widget):
        """ Set the stack widget for this stack item.

        Parameters
        ----------
        widget : QWidget
            The QWidget to use as the stack widget in this item.

        """
        self._stack_widget = widget
        self.layout().addWidget(widget)


class QtStackItem(QtWidgetComponent):
    """ A Qt implementation of an Enaml StackItem.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QStackItem widget.

        """
        return QStackItem(parent)

    def init_layout(self):
        """ Initialize the layout for the underyling widget.

        """
        super(QtStackItem, self).init_layout()
        for child in self.children():
            if isinstance(child, QtContainer):
                self.widget().setStackWidget(child.widget())
                break

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ An overridden visibility setter.

        This setter disables changing visibility on the widget since
        the visibility is controlled entirely by the parent stack.

        """
        pass

