#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from async_messenger import AsyncMessenger
from base_component import BaseComponent


class CommandWidget(AsyncMessenger, BaseComponent):
    """ The base class of all widgets in Enaml.

    This extends BaseComponent with the ability to send and receive
    commands to and from a client widget by mixing in the AsyncMessenger
    class.

    """
    pass

