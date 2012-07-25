#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Unicode


class Document(HasTraits):
    #: The text for the text document
    text = Unicode("")

    #: The editing mode for the document
    mode = Unicode("text")

    #: The title for the document
    title = Unicode("Untitled")

    def as_dict(self):
        """ Return the document as a JSON-serializable dict

        """
        return {
            'text': self.text,
            'mode': self.mode,
            'title': self.title
        }
