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
    #: A private flag to guard trait modifications
    # XXX This seems a bit hackish.
    _setting = Bool(False)

    #: A string provided to implementation clients indicated which type
    #: of widget they should construct. The default type is computed
    #: based on the name of the component class. This may be overridden
    #: by users to define custom behavior, but is typically not needed.
    widget_type = Str

    def _widget_type_default(self):
        """ Computes the type string for widget which should be built
        by implementation clients. The default is simply the name of
        the component class.

        """
        return type(self).__name__

    def build_info(self):
        """ Returns the dictionary of build info for the component tree
        from this point downward.

        """
        info = {}
        info['widget'] = self.widget_type
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

