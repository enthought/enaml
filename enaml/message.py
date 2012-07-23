#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.utils import ObjectDict


class Message(tuple):
    """ A tuple subclass which represents an Enaml protocol message.

    This subclass adds convenience properties for accessing the
    message parts by name instead of postion. It also wraps each
    part of the message as an ObjectDict instead of a plain dict.

    """
    def __new__(cls, parts):
        """ Create a new Message.

        Parameters
        ----------
        parts : iterable
            An iterabled of the four parts to the Enaml message: 
            header, parent_header metadata, and content.

        """
        items = (ObjectDict(part) for part in parts)
        return super(Message, cls).__new__(cls, items)

    @property
    def header(self):
        """ Returns the header of the message as an ObjectDict.

        """
        return self[0]

    @property
    def parent_header(self):
        """ Returns the parent header of the message as an ObjectDict.

        """
        return self[1]

    @property
    def metadata(self):
        """ Returns the metadata of the message as an ObjectDict.

        """
        return self[2]

    @property
    def content(self):
        """ Returns the content of the message as an ObjectDict.

        """
        return self[3]

