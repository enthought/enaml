#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty

from .message import Message
from .utils import ObjectDict


class BaseRequest(object):
    """ An object which represents a request sent by a client.

    This is a base class which contains abstract methods and properties
    which must be implemented by subclasses. Concrete instance of this
    class are passed by a server to its Application instance for 
    handling.

    """
    __metaclass__ = ABCMeta

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    @abstractproperty
    def message(self):
        """ The Message object for this request.

        Returns
        -------
        result : Message
            The Message instance pertaining to this request.

        """
        raise NotImplementedError

    @abstractmethod
    def add_callback(self, callback):
        """ Add a callback to the event queue to be called later.

        This is used by the request handlers to defer long running 
        work until a future time, at which point the results will
        be pushed to the client.

        Parameters
        ----------
        callback : callable
            A callable which should be invoked by the event loop at 
            some future time. This method must return immediately.

        """
        raise NotImplementedError

    @abstractmethod
    def send_reply(self, message):
        """ Send the given message to the client as a reply.

        Parameters
        ----------
        message : Message
            A Message instance to send to the client as a reply to
            this particular request.

        Notes
        -----
        * Users should not usually call this method directly. Instead,
          users should call the 'reply' convenience method. 
        * Calling this method effectively closes the request and further 
          calls to this method will raise an error.

        """
        raise NotImplementedError

    @abstractmethod
    def push_handler(self):
        """ Returns an object that can be used to push unsolicited 
        messages to this client.

        Returns
        -------
        result : BasePushHandler
            A PushHandler instance which can be used to push messages
            to this client, without the client initiating a request.

        """
        raise NotImplementedError

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def reply(self, status='ok', status_msg='', **content):
        """ Create and send a response message to the client.

        Parameters
        ----------
        status : str, optional
            The status of the request. Either 'ok' or 'error'. The
            default is 'ok'.

        status_msg : str, optional
            The status message. This is typically only supplied if
            the status is 'error', and will be a short explanation
            of what went wrong.

        **content
            Other items to add to the 'content' portion of the 
            response message.

        """
        parent_header = self.message.header
        reply_header = ObjectDict(parent_header)
        reply_header.msg_id += '_reply' # XXX do we like this, or should we make a new uuid?
        content = ObjectDict(content)
        content.status = status
        content.status_msg = status_msg
        reply = Message((reply_header, parent_header, ObjectDict(), content))
        self.send_reply(reply)


class BasePushHandler(object):
    """ An object used to push a message to a client.

    Instances of this class should remain functional for the lifetime
    of the client connection.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def push_message(self, message):
        """ Push the given message to the client.

        Parameters
        ----------
        message : Message
            The Message instance that should be pushed to the client.

        """
        raise NotImplementedError

    @abstractmethod
    def add_callback(self, callback):
        """ Add a callback to the event queue to be called later.

        This is used as a convenience for Session objects to provide
        a way to run callables in a deferred fashion. It does not 
        imply any communication with the client. It is merely an
        abstract entry point into the server's event loop. 

        Call it a concession to practicality over purity - SCC

        Parameters
        ----------
        callback : callable
            A callable which should be invoked by the event loop at 
            some future time. This method must return immediately.

        """
        raise NotImplementedError

