#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A module for centralized publishing of messages in an Enaml 
application.

"""
from enaml.core.signaling import Signal


class _hub(object):
    """ A private class which acts as a hub for publishing messages.

    """
    #: The signal to use for publishing messages.
    post = Signal()


#: The global singleton hub.
_hub = _hub()


def post(message):
    """ Post a message to the hub.

    The message will be re-broadcast to all registered hub listeners.

    Parameters
    ----------
    message : dict
        The Enaml message dict to pass to the hub listeners.

    """
    _hub.post(message)


def connect(callback):
    """ Connect a callback to the hub to be called when messages
    are posted to the hub.

    Parameters
    ----------
    callback : callable
        The callable to invoke when a message is posted to the
        hub.

    """
    _hub.post.connect(callback)


def disconnect(callback):
    """ Disconnect the callback from the hub

    A disconnected callback will no longer be invoked when messages
    are posted to the hub.

    Parameters
    ----------
    callback : callable
        The callable that was previously registered with a call
        to 'connect()'.

    """
    _hub.disconnect(callback)

