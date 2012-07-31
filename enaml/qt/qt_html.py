#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QTextEdit
from .qt_constraints_widget import QtConstraintsWidget


class QtHtml(QtConstraintsWidget):
    """ A Qt4 implementation of the Enaml HTML widget.

    """
    def create(self):
        """ Create the underlying widget.

        """
        self.widget = QTextEdit(self.parent_widget)
        self.widget.setReadOnly(True)

    def initialize(self, attrs):
        """ Initialize the widget's attributes.

        """
        super(QtHtml, self).initialize(attrs)
        self.set_source(attrs['source'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_source(self, content):
        """ Handle the 'set_source' action from the Enaml widget.

        """
        self.set_source(content['source'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_source(self, source):
        """ Set the source of the html widget

        """
        self.widget.setHtml(source)

