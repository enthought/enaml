#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import json
from threading import Thread

import zmq
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream

from enaml.messaging.hub import message_hub


class ZMQServerWorker(Thread):
    """ A thread which will run the ZeroMQ IOLoop to dispatch messages
    to and from the Enaml message hub.

    """
    def __init__(self, host, rep_port, pub_port, call_on_main):
        super(ZMQServerWorker, self).__init__()
        self._call_on_main = call_on_main
        self._io_loop = IOLoop.instance()

        ctxt = zmq.Context()
        rep_sock = ctxt.socket(zmq.ROUTER)
        pub_sock = ctxt.socket(zmq.PUB)
        rep_sock.bind(host + ':' + rep_port)
        pub_sock.bind(host + ':' + pub_port)

        self._ctxt = ctxt
        self._rep_sock = rep_sock
        self._pub_sock = pub_sock
        self._rep_stream = ZMQStream(rep_sock)
        self._rep_stream.on_recv(self._on_rep_recv)

    def run(self):
        message_hub.post_message.connect(self._on_message_posted)
        self._io_loop.start()

    def stop(self):
        self._io_loop.stop()
        message_hub.post_message.disconnect(self._on_message_posted)
        self.join()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _on_message_posted(self, message):
        def closure():
            js_message = json.dumps(message)
            self._pub_sock.send(js_message)
        self._io_loop.add_callback(closure)

    def _on_rep_recv(self, mpmsg):
        if len(mpmsg) != 2:
            print 'malformed message', mpmsg
            return
        try:
            msg_id, msg = mpmsg
            message = json.loads(msg)
        except Exception as e:
            print 'json error', message
            return
        try:
            def closure():
                message_hub.deliver_message(message)
            self._call_on_main(closure)
        except Exception as e:
            print 'handler error', e

