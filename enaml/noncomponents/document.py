#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Unicode, Bool, Int, Either


class Document(HasTraits):
    #: The text for the text document
    text = Unicode("")

    #: The editing mode for the document
    mode = Unicode("text")

    #: The title for the document
    title = Unicode("Untitled")

    #: Auto pairs parentheses, braces, etc
    auto_pair = Bool(True)

    #: The editor's font size
    font_size = Int(12)

    #: Display the margin line at a certain column
    margin_line = Either(Int(80), Bool(True))

    def as_dict(self):
        """ Return the document as a JSON-serializable dict

        """
        return {
            'text': self.text,
            'mode': self.mode,
            'title': self.title,
            'auto_pair': self.auto_pair,
            'font_size': self.font_size,
            'margin_line': self.margin_line
        }
