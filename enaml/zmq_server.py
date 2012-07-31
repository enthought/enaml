#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import json

import zmq
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream

from enaml.message import Message
from enaml.request import BaseRequest, BasePushHandler
from enaml.utils import log_exceptions


def pack_message(routing_id, message):
    """ Pack a routing id and Message into a mutlipart zmq message.

    Parameters
    ----------
    routing_id : str
        The zmq socket identity to place first in the message.

    message : Message
        The Message object to serialized into the multipart message.

    """
    multipart = [routing_id]
    dumps = json.dumps
    multipart.extend(dumps(part) for part in message)
    return multipart


def unpack_message(multipart):
    """ Unpack a mutlipart Enaml message received by the server.

    Parameters
    ----------
    multipart : list
        The 5-element list representing the routing_id, header, 
        parent_header, metadata, and content of a client message.

    Returns
    -------
    routing_id, message : str, Message
        The zmq routing id and the deserialized Message object.

    """
    if len(multipart) != 5:
        raise TypeError('Invalid wire message: %s' % multipart)
    routing_id = multipart[0]
    loads = json.loads
    return routing_id, Message(loads(part) for part in multipart[1:])


class ZMQRequest(BaseRequest):
    """ A concrete BaseRequest implementation for the ZMQServer.

    """
    def __init__(self, message, routing_id, stream, ioloop):
        """ Initialize a ZMQRequest.

        Parameters
        ----------
        message : Message
            The Message instance that generated this request.

        routing_id : str
            The zmq identity string for the client.

        stream : ZMQStream
            The zmq socket stream for this request.

        ioloop : IOLoop
            The zmq IOLoop instance for this request.

        """
        self._message = message
        self._routing_id = routing_id
        self._stream = stream
        self._ioloop = ioloop
        self._finished = False

    #--------------------------------------------------------------------------
    # Abstract API implementation
    #--------------------------------------------------------------------------
    @property
    def message(self):
        """ The Message object for this request.

        Returns
        -------
        result : Message
            The Message instance pertaining to this request.

        """
        return self._message

    def add_callback(self, callback):
        """ Add a callback to the event queue to be called later.

        This is can be used by the request handlers to defer long 
        running work until a future time, at which point the results
        can be pushed to the client with the 'push_handler()'.

        Parameters
        ----------
        callback : callable
            A callable which should be invoked by the event loop at 
            some future time. This method will return immediately.

        """
        self._ioloop.add_callback(callback)

    @log_exceptions
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
          calls to this method will log an error.

        """
        if self._finished:
            raise RuntimeError('Request already finished')
        packed = pack_message(self._routing_id, message)
        self._stream.send_multipart(packed)
        self._finished = True

    def push_handler(self):
        """ Returns an object that can be used to push unsolicited 
        messages to this client.

        Returns
        -------
        result : ZMQPushHandler
            A ZMQPushHandler instance which can be used to push messages
            to this client, without the client initiating a request.

        """
        return ZMQPushHandler(self._routing_id, self._stream, self._ioloop)


class ZMQPushHandler(BasePushHandler):
    """ A concrete BasePushHandler implementation for the ZMQServer.

    Instances of this class will remain functional for the lifetime
    of the originating client. If the client disconnects, then 
    this handler will silently drop the messages.

    """
    def __init__(self, routing_id, stream, ioloop):
        """ Initialize a ZMQPushHandler.

        Parameters
        ----------
        routing_id : str
            The zmq identity string for the client.

        stream : ZMQStream
            The zmq socket stream for this push handler.

        ioloop : IOLoop
            The zmq IOLoop instance for this push handler.

        """
        self._routing_id = routing_id
        self._stream = stream
        self._ioloop = ioloop

    @log_exceptions
    def push_message(self, message):
        """ Push the given message to the client.

        Parameters
        ----------
        message : Message
            The Message instance that should be pushed to the client.

        """
        packed = pack_message(self._routing_id, message)
        self._stream.send_multipart(packed)

    def add_callback(self, callback):
        """ Add a callback to the event queue to be called later.

        This is used as a convenience for Session objects to provide
        a way to run callables in a deferred fashion. It does not 
        imply any communication with the client. It is merely an
        abstract entry point into the zmq event loop. 

        Call it a concession to practicality over purity - SCC

        Parameters
        ----------
        callback : callable
            A callable which should be invoked by the event loop at 
            some future time. This method returns immediately.

        """
        self._ioloop.add_callback(callback)


class ZMQServer(object):
    """ An Enaml Application server which uses ZeroMQ sockets.

    """
    def __init__(self, app, host, port):
        """ Initialize a ZMQServer.

        Parameters
        ----------
        app : Application
            The Enaml Application instance which should be served by 
            this server.

        host : string
            The host address for tcp communication. e.g. '127.0.0.1'

        port : int
            The host port to use for communication. e.g. 8888

        """
        ctxt = zmq.Context()
        router = ctxt.socket(zmq.ROUTER)
        router.bind('tcp://%s:%s' % (host, port))
        self._app = app
        self._router = router
        self._stream = ZMQStream(router)
        self._stream.on_recv(self._on_recv)
        self._ioloop = IOLoop.instance()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @log_exceptions
    def _on_recv(self, multipart):
        """ The zmq stream message receive handler.

        Parameters
        ----------
        multipart : list
            The multipart message received by the client.

        """
        routing_id, message = unpack_message(multipart)
        request = ZMQRequest(message, routing_id, self._stream, self._ioloop)
        self._app.handle_request(request)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def start(self):
        """ Start the server's io loop. This call will block until
        the 'stop' method is called.

        """
        self._ioloop.start()

    def stop(self):
        """ Stop the server's io loop. This will cause a previous call
        to 'start' to return.

        """
        self._ioloop.stop()

