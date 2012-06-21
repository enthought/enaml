#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QComboBox
from .qt.QtCore import QStringList, QString
from .qt_control import QtControl

class QtComboBox(QtControl):
    """ A Qt implementation of a combo box
    
    """
    def create(self, parent):
        """ Create the underlying widget

        """
        self.widget = QComboBox(parent)
        self.widget.show()

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes

        """
        self.set_index(init_attrs.get('index', 0))
        self.set_index(init_attrs.get('items'), [])

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
        self.send('selected', {})

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
        q_string_list = QStringList()
        for item in items:
            q_string_list.append(QString(item))
