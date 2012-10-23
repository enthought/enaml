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


ActionPipeInterface.register(QActionPipe)

