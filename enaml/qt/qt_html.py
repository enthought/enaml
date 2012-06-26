#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QTextEdit
from .qt_control import QtControl

class QtHtml(QtControl):
    """ An html display widget based on a QTextEdit

    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QTextEdit(self.parent_widget)

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes

        """
        self.set_source(init_attrs.get('source'))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_source(self, ctxt):
        """ Message handler for set_source

        """
        source = ctxt.get('value')
        if source is not None:
            self.set_source(source)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_source(self, source):
        """ Set the source of the html widget

        """
        self.widget.setHtml(source)
