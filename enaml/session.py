#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from collections import Iterable


class Session(object):
    """ An object representing the session between a client and its 
    Enaml objects.

    The session object is what ensures that each client has their own
    individual instances of objects, so that the only state that is 
    shared between clients is that which is explicitly provided by the
    developer.

    """
    __metaclass__ = ABCMeta

    def __init__(self, session_id, args, kwargs):
        """ Initialize a Session.

        The Session class cannot be used directly. It must be subclassed
        and the subclass must implement the `on_open` method. The user
        can also optionally implement the `init` and `on_close` methods.
        This __init__ method should never be overridden.

        Parameters
        ----------
        session_id : str
            The unique identifier to use for this session.

        username : str
            The username associated with this session.
        
        args : tuple
            Additional arguments passed to the `init` method.
        
        kwargs : tuple
            Additional keyword arguments passed to the `init` method.

        """
        self._session_id = session_id
        self._session_objects = []
        self._pipe_interface = None
        self.init(*args, **kwargs)

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    @abstractmethod
    def on_open(self):
        """ Called by the application when the session is opened.

        This method must be implemented in a subclass and is called to 
        create the Enaml objects for the session. This method will only
        be called once during the session lifetime.
        
        Returns
        -------
        result : iterable
            An iterable of Enaml objects for this session. 

        """
        raise NotImplementedError

    def on_close(self):
        """ Called by the application when the session is closed.

        This method may be optionally implemented by subclasses so that
        they can perform custom cleaup. After this method returns, the 
        session should be considered invalid. This method is only called
        once during the session lifetime. 

        """
        pass

    def init(self, *args, **kwargs):
        """ Perform subclass specific initialization.
        
        This method may be optionally implemented by subclasses so that
        they can perform custom initialization with the arguments passed
        to the factory which created the session. This method is called 
        at the end of the `__init__` method.
        
        Parameters
        ----------
        args
            The positional arguments that were provided by the user to 
            the SessionFactory which created this session.

        kwargs
            The keyword arguments that were provided by the user to the
            SessionFactory which created this session.

        """
        pass

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    @property
    def session_id(self):
        """ The unique identifier for this session.

        Returns
        -------
        result : str
            A unique identifier string for this session.

        """
        return self._session_id

    @property
    def session_objects(self):
        """ The Enaml objects being managed by this session.

        Returns
        -------
        result : tuple
            The Enaml objects in use for the session.

        """
        return self._session_objects

    def snapshot(self):
        """ Get a snapshot of this session.

        Returns
        -------
        result : list
            A list of snapshot dictionaries representing the current 
            state of this session.

        """
        return [obj.snapshot() for obj in self._session_objects]

    def open(self, pipe_interface):
        """ Called by the application when the session is opened.

        This method should never be called by user code.
        
        Parameters
        ----------
        pipe_interface : ActionPipeInterface
            A concreted implementation of ActionPipeInterface for use
            with the Object instances owned by this session.

        """
        self._pipe_interface = pipe_interface
        objs = self.on_open()
        if not isinstance(objs, Iterable):
            objs = (objs,)
        else:
            objs = tuple(objs)
        self._session_objects = objs
        for obj in objs:
            obj.initialize()
            for obj in obj.traverse():
                obj.action_pipe = pipe_interface

    def close(self):
        """ Called by the application when the session is closed.

        """
        # XXX Explicity close the client connection?
        self.on_close()
        for obj in self._session_objects:
            obj.destroy()
        self._session_objects = ()
        
