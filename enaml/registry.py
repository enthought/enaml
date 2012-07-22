#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A module for registering receivers and delivering messages in an
Enaml application.

"""
#: The process-wide registry of message handlers for the application.
_REGISTRY = {}


#: The inverse of the process-wide registry.
_YRTSIGER = {}


def register(target_id, receiver):
    """ Register the receiver for handling messages delivered by 
    the application.

    If a different receiver is already registered with the given
    target id, a ValueError will be raised. Registering the same
    receiver multiple times will raise a ValueError.

    Parameters
    ----------
    target_id : str
        The unique target id for this receiver. Enaml messages can
        be delivered to this receiver at a later time by calling
        the 'deliver' function of the registry.

    receiver : object
        An object that will receive messages. It must have a method 
        named 'receive', which accepts a single argument which is the 
        message dict.

    """
    if receiver in _YRTSIGER:
        raise ValueError("Receiver already registered.")
    if target_id in _REGISTRY:
        raise ValueError("Target id already in use.")
    _REGISTRY[target_id] = receiver
    _YRTSIGER[receiver] = target_id


def unregister(receiver):
    """ Unregister a previously registered receiver. The receiver
    will no longer receive messages from the application.

    Parameters
    ----------
    receiver : object
        An object that was previously registered via a call to the
        'register' method. If the receiver was not previously 
        registered, this is a no-op.

    """
    if receiver in _YRTSIGER:
        target_id = _YRTSIGER.pop(receiver)
        _REGISTRY.pop(target_id, None)


def lookup(target_id):
    """ Return the receiver object for the given target id.

    Parameters
    ----------
    target_id : str
        The identifier for a previously registered receiver.

    Returns
    -------
    result : object
        The receiver object for the identifier, or None if there is
        no registered receiver for the identifier.

    """
    return _REGISTRY.get(target_id)


def all_receivers():
    """ Return all of the current receivers in the registry.

    Returns
    -------
    results : list of tuples
        A list of (target_id, receiver) for all of the registered
        receivers in the application. The order of the list is 
        undefined.

    """
    return _REGISTRY.items()

