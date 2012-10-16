#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Bool, Int

from .control import Control


class TextEditor(Control):
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
    def snapshot(self):
        """ Returns the dict of creation attributes for the control.

        """
        snap = super(TextEditor, self).snapshot()
        snap['text'] = self.text
        snap['mode'] = self.mode
        snap['theme'] = self.theme
        snap['auto_pair'] = self.auto_pair
        snap['font_size'] = self.font_size
        snap['margin_line'] = self.margin_line
        snap['margin_line_column'] = self.margin_line_column
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(TextEditor, self).bind()
        self.publish_attributes('text', 'mode', 'theme', 'auto_pair',
            'font_size', 'margin_line', 'margin_line_column')

