#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from itertools import izip_longest
from uuid import uuid4

from PySide.QtGui import QApplication

from ..core.async_application import AsyncApplication, AbstractBuilder

from qt_message_broker import QMessageBroker
from qt_clients import CLIENTS


class QtLocalClientBuilder(AbstractBuilder):

    def __init__(self, register):
        self._register = register
        self._root = None

    def build(self, info):
        info_stack = [(info, None)]
        while info_stack:
            info_dct, parent = info_stack.pop()
            msg_id = info_dct['msg_id']
            widget_cls = CLIENTS[info_dct['widget']]()
            widget = widget_cls(parent, msg_id)
            if parent is None:
                widget.create(parent)
                widget.initialize(info_dct['attrs'])
                self._root = widget
            else:
                widget.create(parent.widget)
                widget.initialize(info_dct['attrs'])
                parent.add_child(widget)
            self._register(msg_id, widget)
            children = info_dct['children']
            info_stack.extend(izip_longest(children, [], fillvalue=widget))


class QtLocalApplication(AsyncApplication):
    """ An Enaml AsyncApplication which executes in the local process
    and uses Qt to create the client widgets.

    """
    def __init__(self):
        self._qapp = QApplication([])
        self._send_pipe = QMessageBroker()
        self._recv_pipe = QMessageBroker()

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
        return QtLocalClientBuilder(register)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def recv_message(self, msg_id, msg, ctxt):
        return self._recv_pipe.put(msg_id, msg, ctxt)

    def run(self):
        app = self._qapp
        if not getattr(app, '_in_event_loop', False):
            app._in_event_loop = True
            app.exec_()
            app._in_event_loop = False

