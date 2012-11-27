#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging


logger = logging.getLogger(__name__)


def dispatch_action(obj, action, content):
    """ Dispatch an action to a handler method on an object.

    This function will dispatch the action to a handler method named
    `on_action_<action>` where <action> is the provided action.

    Parameters
    ----------
    obj : object
        The object which contains a specially named handler method.

    action : str
        The action to be performed by the object.

    content : dict
        The content dictionary for the action.

    """
    handler_name = 'on_action_' + action
    handler = getattr(obj, handler_name, None)
    if handler is not None:
        handler(content)
    else:
        msg = "Unhandled action '%s' for `%s`"
        logger.warn(msg % (action, obj))

