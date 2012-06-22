#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from itertools import izip_longest

from enaml.async.async_application import AbstractBuilder, AsyncApplication, \
    AsyncApplicationError

from .mock_test_pipe import MockTestPipe

class MockWidget(object):
    """ A mock client UI widget

    """
    def __init__(self, parent, send_pipe, recv_pipe):
        self.parent = parent
        self.send_pipe = send_pipe
        self.recv_pipe = recv_pipe
        self.children = []
        self.attributes = {}
        self.recv_pipe.set_callback(self.recv)

    def initialize(self, attributes):
        # Add receive functions for attributes as needed.
        for k in attributes.iterkeys():
            def recv_func(slf, context):
                setattr(slf, k, context['value'])
            attr_name = 'receive_set_' + k
            if not hasattr(self, attr_name):
                setattr(self, attr_name, recv_func)

        self.attributes.update(attributes)

    def add_child(self, widget):
        self.children.append(widget)

    def send(self, msg, ctxt):
        return self.send_pipe.put(msg, ctxt)

    def recv(self, msg, ctxt):
        handler_name = 'receive_' + msg
        handler = getattr(self, handler_name, None)
        if handler is not None:
            return handler(ctxt)
        return NotImplemented


class MockBuilder(AbstractBuilder):
    """ A builder that generates a client-side UI tree.

    """
    def __init__(self):
        self._root = None

    def build(self, info):
        info_stack = [(info, None)]
        while info_stack:
            info_dct, parent = info_stack.pop()
            send_pipe = info_dct['send_pipe']
            recv_pipe = info_dct['recv_pipe']
            widget_cls = MockWidget
            # Cross the pipes when hooking the MockWidget up to the server widget
            widget = widget_cls(parent, recv_pipe, send_pipe)
            widget.initialize(info_dct['attrs'])
            children = info_dct['children']
            info_stack.extend(izip_longest(children, [], fillvalue=widget))

            # Store a reference to the root widget to prevent things 
            # from being garbage collected
            if parent is None:
                self._root = widget


class MockApplication(AsyncApplication):
    """ A mock application for testing server widget components.

    """
    #--------------------------------------------------------------------------
    # Abstract API implementation
    #--------------------------------------------------------------------------
    def register(self, messenger):
        return (MockTestPipe(), MockTestPipe())

    def builder(self):
        return MockBuilder()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def run(self):
        # XXX How should these get started?
        self._send_pipe.run()
        self._recv_pipe.run()

