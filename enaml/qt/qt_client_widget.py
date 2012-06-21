#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from weakref import ref

from enaml.async.async_application import AsyncApplication


class QtClientWidget(object):

    def __init__(self, parent, msg_id):
        if parent is None:
            self.__parent_ref = lambda: None
        else:
            self.__parent_ref = ref(parent)
            parent.add_child(self)
        self.__msg_id = msg_id
        self.widget = None
        self.children = []

    @property
    def parent(self):
        return self.parent_ref()

    @property
    def msg_id(self):
        return self.__msg_id

    def add_child(self, child):
        self.children.append(child)

    def send(self, msg, ctxt):
        app = AsyncApplication.instance()
        if app is None:
            return
        app.recv_message(self.__msg_id, msg, ctxt)

    def recv(self, msg, ctxt):
        handler_name = 'receive_' + msg
        handler = getattr(self, handler_name, None)
        if handler is not None:
            return handler(ctxt)
        return NotImplemented

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        raise NotImplementedError

    def initialize(self, init_attrs):
        pass

    def bind(self):
        pass

