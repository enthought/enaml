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
