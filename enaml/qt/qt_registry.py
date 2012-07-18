#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A module for registering Qt receivers for an Enaml application.

"""
#: The process-wide registry of message handlers for the application.
_QT_REGISTRY = {}


#: The inverse of the process-wide registry.
_QT_YRTSIGER = {}


def qt_register(messenger_id, messenger):
    """ Register the messenger for receiving messages delivered via
    the messaging hub.

    Parameters
    ----------
    messenger_id : str
        The identifier for the given messenger.

    messenger : object
        An object that will receive messages from the messaging hub.
        It must have a method named 'receive', which accepts a single
        argument which is the message dictionary.

    """
    _QT_REGISTRY[messenger_id] = messenger
    _QT_YRTSIGER[messenger] = messenger_id


def qt_unregister(messenger):
    """ Unregister a previously registered messenger. The messenger
    will no longer receive messages from the messaging hub.

    Parameters
    ----------
    messenger : object
        An object that was previously registered via a call to the
        'register' method. If the messenger was not previously 
        registered, this is a no-op.

    """
    if messenger in _QT_YRTSIGER:
        msgr_id = _QT_YRTSIGER.pop(messenger)
        _QT_REGISTRY.pop(msgr_id, None)


def qt_lookup(messenger_id):
    """ Return the messenger object for the given messenger id.

    Parameters
    ----------
    messenger_id : str
        The identifier for a previously registered messenger.

    Returns
    -------
    result : object
        The messenger object for the identifier, or None if there is
        no registered messenger for the identifier.

    """
    return _QT_REGISTRY.get(messenger_id)


def qt_all_messengers():
    """ Get all the current messengers in the registry.

    Returns
    -------
    results : list of tuples
        A list of (messenger_id, messenger) for all of the registered
        messengers in the application. The order of the list is 
        undefined.

    """
    return _QT_REGISTRY.items()

