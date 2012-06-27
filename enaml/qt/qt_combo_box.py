#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QComboBox
from .qt_constraints_widget import QtConstraintsWidget

class QtComboBox(QtConstraintsWidget):
    """ A Qt implementation of a combo box
    
    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QComboBox(self.parent_widget)

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes

        """
        super(QtComboBox, self).initialize(init_attrs)
        self.set_index(init_attrs.get('index', 0))
        self.set_items(init_attrs.get('items', []))

    def bind(self):
        """ Bind qt signals to slots

        """
        self.widget.currentIndexChanged.connect(self.on_selected)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_selected(self):
        """ Event handler for selected

        """
        self.send('selected', {'value':self.widget.currentIndex()})

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_index(self, ctxt):
        """ Message handler for set_index

        """
        index = ctxt.get('value')
        if index is not None:
            self.set_index(index)

    def receive_set_items(self, ctxt):
        """ Message handler for set_items

        """
        items = ctxt.get('value')
        if items is not None:
            self.set_items(items)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_index(self, index):
        """ Set the current index of the ComboBox

        """
        self.widget.setCurrentIndex(index)

    def set_items(self, items):
        """ Set the items of the ComboBox

        """
        self.widget.clear()
        self.widget.addItems(items)
