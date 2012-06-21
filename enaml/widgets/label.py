#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str, Bool

from .control import Control

class Label(Control):
    """ A simple read-only text display.

    """
    #: The text in the label.
    text = Str

    #: Whether or not the label should wrap around on long lines.
    #: This may not be supported by all toolkit backends (like Wx)
    #: and it may be necessary with those toolkits to insert newline 
    #: characters where necessary.
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
        self.default_send_attr_bind(
                'text', 'word_wrap',
            )

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(Label, self).initial_attrs()
        attrs = {
            'text' : self.text,
            'word_wrap' : self.word_wrap,
        }
        super_attrs.update(attrs)
        return super_attrs

