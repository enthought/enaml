#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import namedtuple
from itertools import izip_longest
from uuid import uuid4

from async_application import AsyncApplication, AsyncApplicationError
from async_reply import AsyncReply, MessageFailure

from PySide.QtGui import QApplication
from PySide.QtCore import Qt, Signal, Slot, QObject


QueuedMessage = namedtuple('QueuedMessage', 'msg_id msg ctxt reply')


class QtMessagePipe(QObject):

    _process = Signal(object)

    def __init__(self):
        super(QtMessagePipe, self).__init__()
        self._receivers = {}
        self._cancelled = set()
        self._process.connect(self._on_process, Qt.QueuedConnection)

    #--------------------------------------------------------------------------
    # Private Api
    #--------------------------------------------------------------------------
    def _cancel_message(self, reply):
        self._cancelled.add(reply)

    @Slot(object)
    def _on_process(self, queued_msg):
        msg_id, msg, ctxt, reply = queued_msg

        cancelled = self._cancelled
        if reply in cancelled:
            cancelled.remove(reply)
            return

        try:
            receiver = self._receivers[msg_id]
        except KeyError:
            raise AsyncApplicationError('Receiver not found')
        
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
        queued_msg = QueuedMessage(msg_id, msg, ctxt, reply)
        self._process.emit(queued_msg)
        return reply

    def add_receiver(self, msg_id, receiver):
        self._receivers[msg_id] = receiver
       

class QtLocalApplication(AsyncApplication):
    """ An Enaml AsyncApplication which executes in the local process
    and uses Qt to create the client widgets.

    """
    def __init__(self):
        self._qapp = QApplication([])
        self._send_pipe = QtMessagePipe()
        self._recv_pipe = QtMessagePipe()

    #--------------------------------------------------------------------------
    # Abstract API implementation
    #--------------------------------------------------------------------------
    def register(self, messenger, id_setter):
        msg_id = uuid4().hex
        id_setter(msg_id)
        self._recv_pipe.add_receiver(msg_id, messenger)

    def send_message(self, msg_id, msg, ctxt):
        return self._send_pipe.put(msg_id, msg, ctxt)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def recv_message(self, msg_id, msg, ctxt):
        return self._recv_pipe.put(msg_id, msg, ctxt)

    #--------------------------------------------------------------------------
    # Sketchy API
    #--------------------------------------------------------------------------
    def create_clients(self, info):
        """ Walks the view tree and creates the necessary clients.

        """
        # NOTE!!!!
        #
        # This is currently hacked together just to validate the ideas of the
        # async message passing, this is certainly not production quality code.
        from qt_clients import CLIENTS
        info_stack = [(info, None)]
        while info_stack:
            info_dct, parent = info_stack.pop()
            widget_cls = CLIENTS[info_dct['widget']]
            widget = widget_cls(info_dct['msg_id'])
            widget.create(parent, info_dct['attrs'])
            self._send_pipe.add_receiver(info_dct['msg_id'], widget)
            children = info_dct['children']
            if children:
                info_stack.extend(izip_longest(children, [], fillvalue=widget.widget))

    def run(self):
        self._qapp.exec_()

