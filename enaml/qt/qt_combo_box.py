#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QComboBox
from .qt_constraints_widget import QtConstraintsWidget


class QtComboBox(QtConstraintsWidget):
    """ A Qt4 implementation of an Enaml ComboBox.
    
    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QComboBox(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget's attributes

        """
        super(QtComboBox, self).initialize(attrs)
        self.set_items(attrs['items'])
        self.set_index(attrs['index'])
        self.widget.currentIndexChanged.connect(self.on_index_changed)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_index(self, content):
        """ Handle the 'set_index' action from the Enaml widget.

        """
        self.set_index(content['index'])

    def on_action_set_items(self, content):
        """ Handle the 'set_items' action from the Enaml widget.

        """
        self.set_items(content['items'])

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_index_changed(self):
        """ The signal handler for the index changed signal.

        """
        content = {'index': self.widget.currentIndex()}
        self.send_action('index_changed', content)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_items(self, items):
        """ Set the items of the ComboBox.

        """
        widget = self.widget
        count = widget.count()
        nitems = len(items)
        for idx, item in enumerate(items[:count]):
            widget.setItemText(idx, item)
        if nitems > count:
            for item in items[count:]:
                widget.addItem(item)
        elif nitems < count:
            for idx in reversed(range(nitems, count)):
                widget.removeItem(idx)

    def set_index(self, index):
        """ Set the current index of the ComboBox

        """
        self.widget.setCurrentIndex(index)

