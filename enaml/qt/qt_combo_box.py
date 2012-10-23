#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QComboBox
from .qt_control import QtControl


class QtComboBox(QtControl):
    """ A Qt implementation of an Enaml ComboBox.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying combo box widget.

        """
        return QComboBox(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtComboBox, self).create(tree)
        self.set_items(tree['items'])
        self.set_index(tree['index'])
        self.widget().currentIndexChanged.connect(self.on_index_changed)

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
        content = {'index': self.widget().currentIndex()}
        self.send_action('index_changed', content)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_items(self, items):
        """ Set the items of the ComboBox.

        """
        widget = self.widget()
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
        self.widget().setCurrentIndex(index)

