#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl

from ...components.label import AbstractTkLabel


class QtLabel(QtControl, AbstractTkLabel):
    """ A Qt implementation of Label.

    """
    #: The internal cached size hint which is used to determine whether
    #: of not a size hint updated event should be emitted when the text
    #: in the label changes
    _cached_size_hint = None

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
        self.set_text(shell.text)
        self.set_word_wrap(shell.word_wrap)
        
    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_text_changed(self, text):
        """ The change handler for the 'text' attribute.

        """
        self.set_text(text)

    def shell_word_wrap_changed(self, word_wrap):
        """ The change handler for the 'word_wrap' attribute.

        """
        self.set_word_wrap(word_wrap)

    def set_text(self, text):
        """ Sets the label on the underlying control.

        """
        self.widget.setText(text)

        # Emit a size hint updated event if the size hint has actually
        # changed. This is an optimization so that a constraints update
        # only occurs when the size hint has actually changed. This 
        # logic must be implemented here so that the label has been
        # updated before the new size hint is computed. Placing this
        # logic on the shell object would not guarantee that the label
        # has been updated at the time the change handler is called.
        cached = self._cached_size_hint
        hint = self._cached_size_hint = self.size_hint()
        if cached != hint:
            self.shell_obj.size_hint_updated()

    def set_word_wrap(self, wrap):
        """ Sets the word wrapping on the underlying widget.

        """
        self.widget.setWordWrap(wrap)

