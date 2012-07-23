#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Bool, Int

from .constraints_widget import ConstraintsWidget


class TextEditor(ConstraintsWidget):
    """ A simple control for displaying read-only text.

    """
    #: The text for the text editor
    text = Unicode("")

    #: The editing mode for the editor
    mode = Unicode("ace/mode/text")

    #: The theme for the editor
    theme = Unicode("ace/theme/textmate")

    #: Auto pairs parentheses, braces, etc
    auto_pair = Bool(True)

    #: The editor's font size
    font_size = Int(12)

    #: Display the margin line
    margin_line = Bool(True)

    #: The column number for the margin line
    margin_line_column = Int(80)

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
        super_attrs['auto_pair'] = self.auto_pair
        super_attrs['font_size'] = self.font_size
        super_attrs['margin_line'] = self.margin_line
        super_attrs['margin_line_column'] = self.margin_line_column
        return super_attrs

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(TextEditor, self).bind()
        self.publish_attributes('text', 'mode', 'theme', 'auto_pair',
            'font_size', 'margin_line', 'margin_line_column')

