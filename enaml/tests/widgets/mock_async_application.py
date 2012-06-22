#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from itertools import izip_longest
from threading import Thread
from uuid import uuid4
from weakref import WeakValueDictionary

from enaml.async.async_application import AbstractBuilder, AsyncApplication, \
    AsyncApplicationError
from enaml.async.async_reply import AsyncReply, MessageFailure


class MockMessenger(object):
    def __init__(self):
        self._receivers = WeakValueDictionary()
        self._cancelled = set()

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

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def put(self, msg_id, msg, ctxt):
        if msg_id not in self._receivers:
            return
        reply = AsyncReply(self._cancel_message)
        queued_msg = (msg_id, msg, ctxt, reply)
        self._process(queued_msg)
        return reply

    def register(self, msg_id, receiver):
        self._receivers[msg_id] = receiver


class MockWidget(object):
    def __init__(self, parent, msg_id):
        self._parent = parent
        self._msg_id = msg_id
        self._children = []
        self._attrs = {}

    def initialize(self, attrs):
        self._attrs.update(attrs)

    def add_child(self, widget):
        self._children.append(widget)


class MockBuilder(AbstractBuilder):
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
    def __init__(self):
        self._send_pipe = MockMessenger()
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
        pass
