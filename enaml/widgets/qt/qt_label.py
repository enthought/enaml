#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl

from ..label import AbstractTkLabel


class QtLabel(QtControl, AbstractTkLabel):
    """ A Qt implementation of Label.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QLabel control.

        """
        self.widget = QtGui.QLabel(parent)

    def initialize(self):
        """ Initializes the attributes on the underlying control.

        """
        super(QtLabel, self).initialize()
        shell = self.shell_obj
        self.set_label(shell.text)
        self.set_word_wrap(shell.word_wrap)
        
    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_text_changed(self, text):
        """ The change handler for the 'text' attribute.

        """
        self.set_label(text)

    def shell_word_wrap_changed(self, word_wrap):
        """ The change handler for the 'word_wrap' attribute.

        """
        self.set_word_wrap(word_wrap)

    def set_label(self, label):
        """ Sets the label on the underlying control.

        """
        self.widget.setText(label)

    def set_word_wrap(self, wrap):
        """ Sets the word wrapping on the underlying widget.

        """
        self.widget.setWordWrap(wrap)

