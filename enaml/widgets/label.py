#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str, Bool, on_trait_change

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
    # Toolkit Communication
    #--------------------------------------------------------------------------
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

    @on_trait_change('text, word_wrap')
    def sync_object_state(self, name, new):
        """ Notify the client component of updates to the object state.

        """
        msg = 'set_' + name
        self.send(msg, {'value':new})

