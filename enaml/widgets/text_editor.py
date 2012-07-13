#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode

from .constraints_widget import ConstraintsWidget


class TextEditor(ConstraintsWidget):
    """ A simple control for displaying read-only text.

    """
    #: The text for the text editor
    text = Unicode

    #: The editing mode for the editor
    mode = Unicode

    #: The theme for the editor
    theme = Unicode

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Returns the dict of creation attributes for the control.

        """
        super_attrs = super(TextEditor, self).creation_attributes()
        super_attrs['text'] = self.text
        super_attrs['mode'] = self.mode
        super_attrs['theme'] = self.theme
        return super_attrs

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(TextEditor, self).bind()
        self.publish_attributes('text', 'mode', 'theme')

