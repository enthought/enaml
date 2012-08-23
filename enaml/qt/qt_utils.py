#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .q_router import QRouter


#: The private QRouter instance used to make deferred calls. The router
#: is created on-demand.
_q_router = None
def q_router():
    """ Return the QRouter used to make deferred calls.

    Returns
    -------
    result : QRouter
        The QRouter being used to make deferred calls by various parts
        of the framework. This is *not* the same router instance that
        is used for message passing.

    """
    global _q_router
    if _q_router is None:
        _q_router = QRouter()
    return _q_router


def deferred_call(callback, *args, **kwargs):
    """ Call a function at some point in the future on the main thread.

    """
    q_router().addCallback(callback, *args, **kwargs)

