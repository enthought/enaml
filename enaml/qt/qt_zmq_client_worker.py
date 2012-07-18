#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import json
from threading import Thread

import zmq
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream

from enaml.qt.qt_hub import qt_message_hub


class QtZMQClientWorker(Thread):
    """ A thread which will run the ZeroMQ IOLoop to dispatch messages
    to the qt_message hub.

    """
    def __init__(self, host, req_port, sub_port):
        super(QtZMQClientWorker, self).__init__()
        self._io_loop = IOLoop.instance()

        ctxt = zmq.Context()
        req_sock = ctxt.socket(zmq.DEALER)
        sub_sock = ctxt.socket(zmq.SUB)

        req_sock.connect(host + ':' + req_port)
        sub_sock.connect(host + ':' + sub_port)
        sub_sock.setsockopt(zmq.SUBSCRIBE, '')

        self._ctxt = ctxt
        self._req_sock = req_sock
        self._sub_sock = sub_sock

        self._req_stream = ZMQStream(req_sock)
        self._sub_stream = ZMQStream(sub_sock)

        self._req_stream.on_recv(self._on_req_recv)
        self._sub_stream.on_recv(self._on_sub_recv)

        qt_message_hub.post_message.connect(self._on_message_posted)

    def run(self):
        self._io_loop.start()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _on_message_posted(self, message):
        def closure():
            js_message = json.dumps(message)
            self._req_stream.send(js_message)
        self._io_loop.add_callback(closure)

    def _on_req_recv(self, mpmsg):
        if len(mpmsg) != 1:
            print 'malformed response', mpmsg

    def _on_sub_recv(self, mpmsg):
        if len(mpmsg) != 1:
            print 'malformed message', mpmsg
            return
        try:
            message = json.loads(mpmsg[0])
        except Exception as e:
            print 'json error', message
            return
        try:
            qt_message_hub.deliver_message.emit(message)
        except Exception as e:
            print 'handler error', e

