#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Bool

from .constraints_widget import ConstraintsWidget


class Label(ConstraintsWidget):
    """ A simple control for displaying read-only text.

    """
    #: The text for the label.
    text = Unicode

    #: Whether or not the label should wrap around on long lines.
    word_wrap = Bool(False)

    #: How strongly a component hugs it's content. Labels hug their
    #: contents' width weakly by default.
    hug_width = 'weak'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the dict of creation attributes for the control.

        """
        snap = super(Label, self).snapshot()
        snap['text'] = self.text
        snap['word_wrap'] = self.word_wrap
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Label, self).bind()
        self.publish_attributes('text', 'word_wrap')

