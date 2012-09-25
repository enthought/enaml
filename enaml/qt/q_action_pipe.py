#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.core.object import ActionPipeInterface

from .qt.QtCore import QObject, Signal


class QActionPipe(QObject):
    """ A messaging pipe implementation.

    This is a small QObject subclass which converts a `send` on the pipe
    into a signal which is connected to by the QtApplication.

    This object also satisfies the Enaml ActionPipeInterface.

    """
    #: A signal emitted when an item has been sent down the pipe.
    actionPosted = Signal(object, object, object)

    def send(self, object_id, action, content):
        """ Send the action to any attached listeners.

        Parameters
        ----------
        object_id : str
            The object id of the target object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        self.actionPosted.emit(object_id, action, content)
    
    def encode_binary(self, bytes):
        """ Encode arbitrary binary data appropriately for this pipe.

        This is an in-process pipe, so this is a no-op.

        Parameters
        ----------
        bytes : bytes
            The raw bytes to encode.

        Returns
        -------
        encoded_bytes : bytes
            The encoded bytes, suitable for transmission over the pipe.
            
        """
        return bytes

    @abstractmethod
    def decode_binary(self, encoded_bytes):
        """ Decode arbitrary binary data appropriately for this pipe.

        This is an in-process pipe, so this is a no-op.

        Parameters
        ----------
        encoded_bytes : str
            The raw bytes to decode.

        Returns
        -------
        bytes : bytes
            The decoded bytes, suitable for use.
            
        """
        return encoded_bytes


ActionPipeInterface.register(QActionPipe)

