#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging
from weakref import ref

from .session import Session
from .utils import id_generator


class Messenger(object):
    """ A class which handles communication with a Session.

    A messenger provides an api for passing messages to and from an
    object which lives on a client. The messages are routed through
    the Session which owns this messenger.

    """
    #: A readonly property which returns the instance's class name.
    #: This name is used as the key in the client session's factory dictionary.
    @property
    def class_name(self):
        return type(self).__name__

    #: A readonly property which returns the instance's base class names.
    # XXX this is needed mainly for compatibility with the Declarative
    # infrastructure - remove?
    @property
    def base_names(self):
        return [type(self).__name__]

    #: The default object id generator. This can be overridden in a
    #: subclass to provide custom unique messenger identifiers.
    object_id_generator = id_generator('o')

    def object_id():

        def getter(self):
            try:
                res = self.__object_id
            except AttributeError:
                res = self.__object_id = self.object_id_generator.next()
            return res

        return (getter,)

    #: A read-only property which returns the object id. This identifier
    #: is *not* by default a uuid. This was deliberately chosen to reduce
    #: the size of the messages sent across the wire. Most messages tend 
    #: to be small enough that a uuid would double the size. If true 
    #: uniqueness is required for a particular use case, then the object 
    #: id generator can be overridden in a given subclass.
    object_id = property(*object_id())

    def session():

        def getter(self):
            try:
                sref = self.__session_ref
            except AttributeError:
                sref = self.__session_ref = lambda: None
            return sref()

        def setter(self, session):
            if not isinstance(session, Session):
                msg = 'Expected a Session. Got object of type `%s` instead.'
                raise TypeError(msg % type(session).__name__)
            # XXX unregister messenger?
            self.__session_ref = ref(session)
            session.register_widget(self) #XXX should be 'register_object'

        def deleter(self):
            # XXX unregister messenger?
            self.__session_ref = lambda: None

        return (getter, setter, deleter)

    #: A property which handles the Session which owns this Messenger.
    #: Only a weakref is stored for the Session to ameliorate issues
    #: with reference cycles.
    session = property(*session())

    #--------------------------------------------------------------------------
    # Messaging/Session API
    #--------------------------------------------------------------------------
    def handle_action(self, action, content):
        """ Handle an action sent from the client of this messenger.

        This is called by the messenger's Session object when the client
        of the messenger sends it a message. The default behavior of the 
        method is to dispatch the message to a handler method named with
        the name 'on_action_<action>' where <action> is substituted with
        the message action.

        Parameters
        ----------
        action : str
            The action to be performed by the messenger.

        content : ObjectDict
            The content dictionary for the action.

        """
        handler_name = 'on_action_' + action
        handler = getattr(self, handler_name, None)
        if handler is not None:
            handler(content)
        else:
            # XXX probably want to raise an exception so the Session
            # can convert it into an error response.
            # XXX make this logging more configurable
            msg = "Unhandled action '%s' sent to messenger %s:%s"
            name = type(self.__name__)
            logging.warn(msg % (action, name, self.object_id))

    def send_action(self, action, content):
        """ Send an action to the client of this messenger.

        This method can be called to send an unsolicited message of
        type 'action' to the client of this messenger.

        Parameters
        ----------
        action : str
            The action for the message.

        content : dict
            The content of the message.

        """
        session = self.session
        if session is None:
            # XXX make this logging more configurable
            msg = 'No Session object for messenger %s:%s'
            name = type(self).__name__
            logging.warn(msg % (name, self.object_id))
        else:
            session.send_action(self.object_id, action, content)


    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ A method which takes a snapshot of the current state of the object.

        """
        snap = super(Messenger, self).snapshot()
        snap['class'] = self.class_name
        snap['bases'] = self.base_names
        snap['object_id'] = self.object_id
        return snap

    def bind(self):
        """ A method which is called when a widget is published in a session
        
        The intent of this is to provide a hook for subclasses to bind trait
        notifications and other callbacks to send messages through the session.
        This is assumed to be called only once.
        
        """
        pass
