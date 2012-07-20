#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, ReadOnly, Str

from enaml.core.base_component import BaseComponent
from enaml.messaging import hub
from enaml.messaging.registry import register
from enaml.utils import LoopbackGuard, id_generator


id_gen = id_generator('w')


class MessengerWidget(BaseComponent):
    """ The base class of all widget classes in Enaml.

    This extends BaseComponent with the ability to send and receive
    commands to and from a target by mixing in the AsyncMessenger
    class. It aslo provides the necessary data members and methods
    required to initialize the client widget.

    """
    #: The storage for the widget target id.
    target_id = ReadOnly

    #: A loopback guard which can be used to prevent a loopback cycle
    #: of messages when setting attributes from within a handler.
    loopback_guard = Instance(LoopbackGuard, ())

    #: A string used to speficy the type of widget which should be 
    #: created by clients when this widget is published. The default 
    #: type is computed based on the name of the component class. This 
    #: may be overridden by users as needed to define custom behavior.
    widget_type = Str
    def _widget_type_default(self):
        return type(self).__name__

    def __new__(cls, *args, **kwargs):
        self = super(MessengerWidget, cls).__new__(cls, *args, **kwargs)
        self.target_id = id_gen.next()
        register(self.target_id, self)
        return self

    def traits_init(self):
        super(MessengerWidget, self).traits_init()
        self.bind()

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def receive(self, message):
        if message['type'] == 'message':
            self.receive_message(message)

    def receive_message(self, message):
        payload = message['payload']
        handler_name = 'on_message_' + payload['action'].replace('-', '_')
        handler = getattr(self, handler_name, None)
        if handler is not None:
            handler(payload)

    def send_message(self, payload):
        msg = {
            'target_id': self.target_id,
            'operation_id': None,
            'type': 'message',
            'payload': payload,
        }
        hub.post(msg)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    @property
    def parent_id(self):
        """ A read only property which returns the target id of the 
        parent of this messenger.

        Returns
        -------
        result : str or None
            The target id of the parent messenger, or None if the parent
            is not an instance of MessengerWidget.

        """
        parent = self.parent
        if isinstance(parent, MessengerWidget):
            return parent.target_id

    def creation_tree(self):
        tree = self.creation_payload()
        children = [c.creation_tree() for c in self.children]
        tree['children'] = children
        return tree

    def creation_payload(self):
        """ Returns the payload dict for the 'create' action for the
        messenger.

        Returns
        -------
        results : dict
            The creation payload dict for the messenger widget.

        """
        payload = {}
        payload['target_id'] = self.target_id
        payload['action'] = 'create'
        payload['type'] = self.widget_type
        payload['parent_id'] = self.parent_id
        payload['attributes'] = self.creation_attributes()
        return payload

    def creation_attributes(self):
        """ Returns a dictionary of attributes to initialize the state
        of the target widget when it is created. 

        This method is called by 'creation_info' when assembling the
        dictionary of initial state for creation of the client.

        This method returns a a new empty dictionary which should be 
        updated in-place by subclasses before being returned to the
        caller.

        Returns
        -------
        results : dict

        """
        return {}

    def bind(self):
        """ A method which should be called when preparing a widget for
        publishing.

        The intent of this method is to allow a widget to hook up its
        trait change notification handlers which will send messages
        to the client. The default implementation of this method is 
        a no-op, but is provided to be super() friendly. It's assumed
        that this method will only be called once by the object which
        manages the process of preparing a widget for publishing.

        """
        pass

    def publish_attributes(self, *attrs):
        """ A convenience method provided for subclasses to use to 
        publish an arbitrary number of attributes to the target widet.

        The action generated for the target message is created by 
        prefixing 'set-' to the name of the changed attribute. This
        method is not intended to meet the needs of *all* attribute
        publishing. Rather it is meant to handle the majority of 
        simple cases. More complex attributes will need to implement
        their own dispatching handlers.

        Parameters
        ----------
        *attrs
            The string names of the attributes to publish to the client.
            These attributes are expected to be simply serializable.
            More complex values should use their own dispatch handlers.

        """
        otc = self.on_trait_change
        handler = self._publish_attr_handler
        for attr in attrs:
            otc(handler, attr)

    def set_guarded(self, **attrs):
        """ A convenience method provided for subclasses to set a
        sequence of attributes from within a loopback guard.

        Parameters
        ----------
        **attrs
            The attributes which should be set on the component from
            within a loopback guard context.

        """
        with self.loopback_guard(*attrs):
            for name, value in attrs.iteritems():
                setattr(self, name, value)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _publish_attr_handler(self, name, new):
        """ A trait change handler which will send an attribute change
        message to a target by prefixe the attr name with 'set-' in 
        order to creation the action name.

        The value of the attribute is expected to be serializable.
        If the loopback guard is held for the given name, then the 
        message will no be sent (avoiding potential loopbacks).

        """
        if name not in self.loopback_guard:
            action = 'set-' + name
            payload = {'action': action, name: new}
            self.send_message(payload)

