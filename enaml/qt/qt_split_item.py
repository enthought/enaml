#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QWidget
from .q_single_widget_layout import QSingleWidgetLayout
from .qt_container import QtContainer
from .qt_widget_component import QtWidgetComponent


class QSplitItem(QWidget):
    """ A QWidget subclass which acts as an item QSplitter.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a QSplitItem.

        Parameters
        ----------
        *args, **kwargs
            The position and keyword arguments required to initialize
            a QWidget.

        """
        super(QSplitItem, self).__init__(*args, **kwargs)
        self._split_widget = None
        self.setLayout(QSingleWidgetLayout())

    def splitWidget(self):
        """ Get the split widget for this split item.

        Returns
        -------
        result : QWidget or None
            The split widget being managed by this item.

        """
        return self._split_widget

    def setSplitWidget(self, widget):
        """ Set the split widget for this split item.

        Parameters
        ----------
        widget : QWidget
            The QWidget to use as the split widget in this item.

        """
        self._split_widget = widget
        self.layout().addWidget(widget)


class QtSplitItem(QtWidgetComponent):
    """ A Qt implementation of an Enaml SplitItem.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QStackItem widget.

        """
        return QSplitItem(parent)

    def create(self, tree):
        """ Create and initialize the underyling widget.

        """
        super(QtSplitItem, self).create(tree)
        self.set_preferred_size(tree['preferred_size'])

    def init_layout(self):
        """ Initialize the layout for the underyling widget.

        """
        super(QtSplitItem, self).init_layout()
        for child in self.children():
            if isinstance(child, QtContainer):
                self.widget().setSplitWidget(child.widget())
                break

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtSplitItem.

        """
        for child in self.children():
            if isinstance(child, QtContainer):
                self.widget().setSplitWidget(child.widget())
                break

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_preferred_size(self, content):
        """ Handle the 'set_preferred_size' action from the Enaml widget.

        """
        self.set_preferred_size(content['preferred_size'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_preferred_size(self, size):
        """ Set the preferred size for this item in the splitter.

        """
        # XXX implement me
        pass

