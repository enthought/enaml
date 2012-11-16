#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from types import MethodType


def make_handler_func(func_name, name, obj):
    func = lambda slf, ctxt: setattr(slf, name, ctxt['value'])
    func.func_name = func_name
    return MethodType(func, obj)


class MockWidget(object):
    """ A mock client UI widget

    """
    def __init__(self, widget_type, parent, send_pipe, recv_pipe):
        self.widget_type = widget_type
        self.parent = parent
        self.send_pipe = send_pipe
        self.recv_pipe = recv_pipe
        self.children = []
        self.attributes = {}
        self.recv_pipe.set_callback(self.recv)
        if parent is not None:
            parent.add_child(self)

    def initialize(self, attributes):
        # Add receive functions for attributes as needed.
        for k in attributes.iterkeys():
            func_name = 'receive_set_' + k
            recv_func = make_handler_func(func_name, k, self)
            if not hasattr(self, func_name):
                setattr(self, func_name, recv_func)

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
        elif 'set' not in msg and not hasattr(self, msg):
            setattr(self, msg, True)
            return None
        return NotImplemented


