#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str

from enaml.async.async_messenger import AsyncMessenger
from enaml.core.base_component import BaseComponent


class MessengerWidget(AsyncMessenger, BaseComponent):
    """ The base class of all widgets in Enaml.

    This extends BaseComponent with the ability to send and receive
    commands to and from a client widget by mixing in the AsyncMessenger
    class.

    """
    # This is a hack so that the message id can be set by the async
    # messenger class (since we inherit HasStrictTraits)
    # XXX we need to make this better.
    _AsyncMessenger__msg_id = Str

    #: The widget class name
    widget_name = Str

    #: A private flag to guard trait modifications
    # XXX This seems a bit hackish.
    _setting = Bool(False)

    def _widget_name_default(self):
        return type(self).__name__

    def build_info(self):
        """ Returns the dictionary of build information for this tree
        from this point downward.

        """
        info = {}
        info['widget'] = self.widget_name
        info['msg_id'] = self.msg_id
        info['attrs'] = self.initial_attrs()
        child_info = []
        for child in self.children:
            child_info.append(child.build_info())
        info['children'] = child_info
        return info

    def initial_attrs(self):
        """ Returns a dictionary of attributes to initialize on the
        client widget.

        XXX - document what types of things to put in this dict.

        """
        return {}

