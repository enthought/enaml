#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import json

import zmq
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream

from enaml.messaging.hub import message_hub
from enaml.messaging.registry import register


class ZMQApplication(object):
    """ An Enaml AsyncApplication which executes in the local process
    and uses Qt to create the client items.

    Since this is a locally running application, the Enaml messaging
    protocol is short-circuited in a few ways:
        1) No messages are serialized to json. The are transferred 
           between objects in their dictionary form since the 
           serialization step is entirely unnecessary.
        2) No messages are generated for the creation of widgets when
           they are published. The application just directly creates
           the widgets.

    """
    def __init__(self, host, rep_port, pub_port):
        self._io_loop = IOLoop.instance()
        self._views = {}

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

        def app_id():
            yield 'app'
        register(self, app_id())

        message_hub.post_message.connect(self._on_posted_message)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def receive(self, message):
        payload = message['payload']
        if payload['action'] == 'create':
            view_name = payload['name']
            view = self._views[view_name]
            tree = view.creation_tree()
            message = {
                'type': 'message',
                'target_id': 'app',
                'operation_id': message['operation_id'],
                'payload': {
                    'action': 'create',
                    'tree': tree,
                }
            } 
            message_hub.post_message(message)

    def _on_posted_message(self, message):
        js_message = json.dumps(message)
        self._pub_sock.send(js_message)

    def _on_rep_recv(self, mpmsg):
        message = None
        if len(mpmsg) != 2:
            reply = {'status': 'error'}
        else:
            try:
                mid, msg = mpmsg
                message = json.loads(msg)
            except Exception as e:
                print 'json error', message
                reply = {'status': 'error'}
            else:
                reply = {'status': 'ok'}
        self._rep_stream.send_multipart([mid, json.dumps(reply)])
        try:
            message_hub.deliver_message(message)
        except Exception as e:
            print 'handler error', e

    #--------------------------------------------------------------------------
    # Application API
    #--------------------------------------------------------------------------
    def serve(self, name, view):
        self._views[name] = view

    def mainloop(self):
        """ Enter the mainloop of the application.

        """
        self._io_loop.start()

    def exit(self):
        """ Exit the mainloop of the application.

        """
        self._io_loop.stop()

