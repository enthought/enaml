#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A module for registering message receivers for an Enaml application.

"""
from enaml.utils import id_generator


#: The process-wide registry of message handlers for the application.
_REGISTRY = {}


#: The inverse of the process-wide registry.
_YRTSIGER = {}


def register(messenger, id_gen=id_generator('msgr')):
    """ Register the messenger for receiving messages delivered via
    the messaging hub.

    Calling this method multiple times with the same messenger will
    return the same value until the messenger is unregistered.

    Parameters
    ----------
    messenger : object
        An object that will receive messages from the messaging hub.
        It must have a method named 'receive', which accepts a single
        argument which is the message dictionary.

    id_gen : generator, optional
        A generator whose 'next()' method will be called to generate
        the messaging identifer for the messenger. The default will
        create monontonically increasing identifiers. If the default
        is overridden, it should ensure the uniqueness of its values.

    Returns
    -------
    result : str
        The identifier string to use when sending messages to and from
        the messenger.

    """
    if messenger in _YRTSIGER:
        return _YRTSIGER[messenger]
    msgr_id = id_gen.next()
    _REGISTRY[msgr_id] = messenger
    _YRTSIGER[messenger] = msgr_id
    return msgr_id


def unregister(messenger):
    """ Unregister a previously registered messenger. The messenger
    will no longer receive messages from the messaging hub.

    Parameters
    ----------
    messenger : object
        An object that was previously registered via a call to the
        'register' method. If the messenger was not previously 
        registered, this is a no-op.

    """
    if messenger in _YRTSIGER:
        msgr_id = _YRTSIGER.pop(messenger)
        _REGISTRY.pop(msgr_id, None)


def lookup(messenger_id):
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
    return _REGISTRY.get(messenger_id)


def all_messengers():
    """ Get all the current messengers in the registry.

    Returns
    -------
    results : list of tuples
        A list of (messenger_id, messenger) for all of the registered
        messengers in the application. The order of the list is 
        undefined.

    """
    return _REGISTRY.items()

