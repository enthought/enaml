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
    def creation_attributes(self):
        """ Returns the dict of creation attributes for the control.

        """
        super_attrs = super(Label, self).creation_attributes()
        super_attrs['text'] = self.text
        super_attrs['word_wrap'] = self.word_wrap
        return super_attrs

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Label, self).bind()
        self.publish_attributes('text', 'word_wrap')

