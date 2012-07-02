#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QLabel
from .qt_constraints_widget import QtConstraintsWidget

class QtLabel(QtConstraintsWidget):
    """ An label widget based on a QLabel

    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QLabel(self.parent_widget)

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes

        """
        super(QtLabel, self).initialize(init_attrs)
        self.set_text(init_attrs.get('text', ''))
        self.set_word_wrap(init_attrs.get('word_wrap', False))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_text(self, ctxt):
        """ Message handler for set_text

        """
        text = ctxt.get('text')
        if text is not None:
            self.set_text(text)

    def receive_set_word_wrap(self, ctxt):
        """ Message handler for set_word_wrap

        """
        wrap = ctxt.get('word_wrap')
        if wrap is not None:
            self.set_word_wrap(wrap)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the source of the label widget

        """
        self.widget.setText(text)

    def set_word_wrap(self, wrap):
        """ Set the word wrap of the label widget

        """
        self.widget.setWordWrap(wrap)
        
