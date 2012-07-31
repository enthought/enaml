#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty

from .message import Message
from .utils import id_generator


#: The global id generation for repsonse messages.
_response_id_gen = id_generator('rmsg_')


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
    def send_response(self, message):
        """ Send the given message to the client as a reply.

        Parameters
        ----------
        message : Message
            A Message instance to send to the client as a reply to
            this particular request.

        Notes
        -----
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
    # Convenience API
    #--------------------------------------------------------------------------
    def send_ok_response(self, metadata=None, content=None):
        """ A convenience method to send an "ok" message reponse for 
        this given request.

        Parameters
        ----------
        metadata : dict, optional
            Any metadata to send with the response.

        content : dict, optional
            Additional content to send with the response.

        """
        parent_header = self.message.header
        header = {
            'session': parent_header.session,
            'username': parent_header.username,
            'msg_id': _response_id_gen.next(),
            'msg_type': parent_header.msg_type + '_response',
            'version': parent_header.version,
        }
        metadata = metadata or {}
        content = content or {}
        content['status'] = 'ok'
        content['status_msg'] = ''
        message = Message((header, parent_header, metadata, content))
        self.send_response(message)

    def send_error_response(self, status_msg, metadata=None, content=None):
        """A convenience method to send an "error" message response for 
        this request.

        Parameters
        ----------
        status_msg : str
            The status message to use in the error response.

        metadata : dict, optional
            Any metadata to send with the response.

        content : dict, optional
            Additional content to send with the response.

        """
        parent_header = self.message.header
        header = {
            'session': parent_header.session,
            'username': parent_header.username,
            'msg_id': _response_id_gen.next(),
            'msg_type': parent_header.msg_type + '_response',
            'version': parent_header.version,
        }
        metadata = metadata or {}
        content = content or {}
        content['status'] = 'error'
        content['status_msg'] = status_msg
        message = Message((header, parent_header, metadata, content))
        self.send_response(message)


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

