#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QTextEdit
from .qt_constraints_widget import QtConstraintsWidget

class QtHtml(QtConstraintsWidget):
    """ An html display widget based on a QTextEdit

    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QTextEdit(self.parent_widget)

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes

        """
        super(QtHtml, self).initialize(init_attrs)
        self.set_source(init_attrs.get('source', ''))
        self.set_read_only(init_attrs.get('read_only', False))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_source(self, ctxt):
        """ Message handler for set_source

        """
        source = ctxt.get('source')
        if source is not None:
            self.set_source(source)

    def receive_set_read_only(self, ctxt):
        """ Message handler for set_read_only

        """
        read_only = ctxt.get('read_only')
        if read_only is not None:
            self.set_read_only(read_only)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_source(self, source):
        """ Set the source of the html widget

        """
        self.widget.setHtml(source)

    def set_read_only(self, read_only):
        """ Set whether or not the widget is editable

        """
        self.widget.setReadOnly(read_only)
