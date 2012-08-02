#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
"""
Session Handler
===============

The application object expects session handlers to have the
following attributes:

session_name : string
    A unique, human-friendly name.

session_description : string
    A brief description of the session.

The session handler should also be callable, where the call is given
a start_session request, and returns an instance of a Session.

While in many cases this may be an instance of the SessionHandler class,
does not need to be the case.

"""


class SessionHandler(object):
    """ Callable that can create a new session from a Session subclass
    
    """
    
    def __init__(self, session_name, session_description, session_class, *args, **kwargs):
        """ Initialize a SessionHandler
        
        Parameters
        ----------
        session_name : string
            A unique, human-friendly name.
        
        session_description : string
            A brief description of the session.
        
        session_class : Session subclass object
            A subclass of Session that this handler creates
        
        args : tuple
            Optional positional arguments to be passed to the Session's
            initialize() method
        
        kwargs : dict
            Optional keyword arguments to be passed to the Session's
            initialize() method
        
        """
        self.session_name = session_name
        self.session_description = session_description
        self.session_class = session_class
        self.args = args
        self.kwargs = kwargs
    
    def __call__(self, request):
        """ Create an instance of the Session subclass
        
        """
        push_handler = request.push_handler()
        username = request.message.header.username
        session = self.session_class(push_handler, username, self.args,
            self.kwargs)
        return session
