#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from itertools import izip_longest
from threading import Condition, Thread
from uuid import uuid4
from weakref import WeakValueDictionary

from enaml.async.async_application import AbstractBuilder, AsyncApplication, \
    AsyncApplicationError
from enaml.async.async_reply import AsyncReply, MessageFailure


class MockMessenger(object):
    def __init__(self):
        self._receivers = WeakValueDictionary()
        self._cancelled = set()
        self._messages = list()
        self._queue_lock = Condition()

    #--------------------------------------------------------------------------
    # Private Api
    #--------------------------------------------------------------------------
    def _cancel_message(self, reply):
        self._cancelled.add(reply)

    def _process(self, queued_msg):
        msg_id, msg, ctxt, reply = queued_msg

        cancelled = self._cancelled
        if reply in cancelled:
            cancelled.remove(reply)
            return

        try:
            receiver = self._receivers[msg_id]
        except KeyError:
            return # Log this instead.

        try:
            result = receiver.recv(msg, ctxt)
        except Exception as exc:
            # XXX better exception message trapping
            result = MessageFailure(msg_id, msg, ctxt, exc.message)

        reply.finished(result)

    def _main_loop(self):
        """ Run the main loop of this messenger.

        """
        ql = self._queue_lock

        while True:
            ql.acquire()
            while len(self._messages) == 0:
                ql.wait()
            self._process(self._messages.pop(0))
            ql.release()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def put(self, msg_id, msg, ctxt):
        if msg_id not in self._receivers:
            return
        reply = AsyncReply(self._cancel_message)
        queued_msg = (msg_id, msg, ctxt, reply)

        ql = self._queue_lock
        ql.acquire()
        self._messages.append(queued_msg)
        ql.notify()
        ql.release()

        return reply

    def register(self, msg_id, receiver):
        self._receivers[msg_id] = receiver

    def run(self):
        self.thread = Thread(target=self._main_loop)
        self.thread.daemon = True
        self.thread.start()


class MockWidget(object):
    """ A mock client UI widget

    """
    def __init__(self, parent, msg_id):
        self._parent = parent
        self._msg_id = msg_id
        self._children = []
        self._attrs = {}

    def initialize(self, attrs):
        self._attrs.update(attrs)

    def add_child(self, widget):
        self._children.append(widget)

    def send(self, msg, ctxt):
        app = AsyncApplication.instance()
        if app is None:
            return
        app.recv_message(self._msg_id, msg, ctxt)

    def recv(self, msg, ctxt):
        handler_name = 'receive_' + msg
        handler = getattr(self, handler_name, None)
        if handler is not None:
            return handler(ctxt)
        return NotImplemented


class MockBuilder(AbstractBuilder):
    """ A builder that generates a client-side UI tree.

    """
    def __init__(self, register):
        self._register = register
        self._root = None

    def build(self, info):
        info_stack = [(info, None)]
        while info_stack:
            info_dct, parent = info_stack.pop()
            msg_id = info_dct['msg_id']
            widget = MockWidget(parent, msg_id)
            if parent is None:
                widget.initialize(info_dct['attrs'])
                self._root = widget
            else:
                widget.initialize(info_dct['attrs'])
                parent.add_child(widget)
            self._register(msg_id, widget)
            children = info_dct['children']
            info_stack.extend(izip_longest(children, [], fillvalue=widget))


class MockApplication(AsyncApplication):
    """ An application

    """
    def __init__(self):
        # server -> client
        self._send_pipe = MockMessenger()
        # client -> server
        self._recv_pipe = MockMessenger()

    #--------------------------------------------------------------------------
    # Abstract API implementation
    #--------------------------------------------------------------------------
    def register(self, messenger, id_setter):
        msg_id = uuid4().hex
        id_setter(msg_id)
        self._recv_pipe.register(msg_id, messenger)

    def send_message(self, msg_id, msg, ctxt):
        return self._send_pipe.put(msg_id, msg, ctxt)

    def builder(self):
        def register(msg_id, client):
            self._send_pipe.register(msg_id, client)
        return MockBuilder(register)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def recv_message(self, msg_id, msg, ctxt):
        return self._recv_pipe.put(msg_id, msg, ctxt)

    def run(self):
        self._send_pipe.run()
        self._recv_pipe.run()

