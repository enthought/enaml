#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
import logging
import uuid

from enaml.core.object import Object


class Application(object):
    """ The application object which manages the top-level communication
    protocol for serving Enaml views.

    """
    __metaclass__ = ABCMeta

    #: The singleton application instance
    _instance = None

    @staticmethod
    def instance():
        """ Get the global Application instance.

        Returns
        -------
        result : Application or None
            The global application instance, or None if one has not yet
            been created.

        """
        return Application._instance

    def __new__(cls, *args, **kwargs):
        """ Create a new Enaml Application.

        There may be only one application instance in existence at any
        point in time. Attempting to create a new Application when one
        exists will raise an exception.

        """
        if Application.instance() is not None:
            raise RuntimeError('An Application instance already exists')
        self = super(Application, cls).__new__(cls)
        Application._instance = self
        return self

    def __init__(self, factories):
        """ Initialize an Enaml Application.

        Parameters
        ----------
        factories : iterable
            An iterable of SessionFactory instances that will be used
            to create the sessions for the application.

        """
        self._all_factories = []
        self._named_factories = {}
        self._sessions = {}
        self.add_factories(factories)
    
    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    @abstractmethod
    def pipe_interface(self):
        """ An abstractmethod which returns the ActionPipeInterface for
        the application.

        """
        raise NotImplementedError

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def add_factories(self, factories):
        """ Add session factories to the application.

        Parameters
        ----------
        factories : iterable
            An iterable of SessionFactory instances to add to the 
            application.

        """
        all_factories = self._all_factories
        named_factories = self._named_factories
        for factory in factories:
            name = factory.name
            if name in named_factories:
                msg = 'Multiple session factories named `%s`; ' % name
                msg += 'replacing previous value.'
                logging.warn(msg)
                old_factory = named_factories.pop(name)
                all_factories.remove(old_factory)
            all_factories.append(factory)
            named_factories[name] = factory

    def discover(self):
        """ Get a dictionary of session information for the application.

        Returns
        -------
        result : list
            A list of dicts of information about the available sessions.

        """
        info = [
            {'name': fact.name, 'description': fact.description} 
            for fact in self._all_factories
        ]
        return info

    def start_session(self, name):
        """ Start a new session of the given name.

        This method will create a new session object for the requested
        session type and return the new session_id. If the session name
        is invalid, an exception will be raised.

        Parameters
        ----------
        name : str
            The name of the session to start.

        Returns
        -------
        result : str
            The unique identifier for the created session.

        """
        if name not in self._named_factories:
            raise ValueError('Invalid session name')
        factory = self._named_factories[name]
        session_id = uuid.uuid4().hex
        session = factory(session_id)
        self._sessions[session_id] = session
        session.open(self.pipe_interface())
        return session_id

    def end_session(self, session_id):
        """ End the session with the given session id.

        This method will close down the existing session. If the session
        id is not valid, an exception will be raised.

        Parameters
        ----------
        session_id : str
            The unique identifier for the session to close.

        """
        if session_id not in self._sessions:
            raise ValueError('Invalid session id')
        session = self._sessions.pop(session_id)
        session.close()

    def snapshot(self, session_id):
        """ Get a snapshot of the Session with the given session_id.

        Parameters
        ----------
        session_id : str
            The unique identifier for the given session.

        Returns
        -------
        result : list
            A list of snapshot dictionaries for the given session.

        """
        session = self._sessions.get(session_id)
        if session is None:
            raise ValueError('Invalid session id')
        return session.snapshot()

    def dispatch_object_message(self, object_id, action, content):
        """ Dispatch a message to an object with the given id.

        This method can be called by subclasses when they receive an
        object action message from a client object. If the object does
        not exist, an exception will be raise.

        Parameters
        ----------
        object_id : str
            The unique identifier for the object.

        action : str
            The action to be performed by the object.

        content : dict
            The dictionary of content needed to perform the action.

        """
        obj = Object.lookup_object(object_id)
        if obj is None:
            raise ValueError('Invalid object id')
        obj.handle_action(action, content)

    def destroy(self):
        """ Destroy this application instance. 

        Only after an application is destroyed will it be possible to 
        create a new application instance.

        """
        for session in self._sessions.itervalues():
            session.close()
        self._all_factories = []
        self._named_factories = {}
        self._sessions = {}
        Application._instance = None

