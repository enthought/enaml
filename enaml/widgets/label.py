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
    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Label, self).bind()
        self.default_send('text', 'word_wrap')

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(Label, self).initial_attrs()
        attrs = {'text' : self.text, 'word_wrap' : self.word_wrap}
        super_attrs.update(attrs)
        return super_attrs

