#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from itertools import count, izip_longest

from enaml.async.async_application import AsyncApplication, AbstractBuilder

from .qt.QtGui import QApplication
from .qt_clients import CLIENTS
from .qt_local_pipe import QtLocalPipe


class QtLocalClientBuilder(AbstractBuilder):

    def __init__(self):
        self._root = None

    def build(self, info):
        info_stack = [(info, None)]
        while info_stack:
            info_dct, parent = info_stack.pop()

            # Unpack the identifier information from the dict
            uuid = info_dct['uuid']
            send_pipe = info_dct['send_pipe']
            recv_pipe = info_dct['recv_pipe']

            # Load the widget class that will be used.
            widget_cls = CLIENTS[info_dct['widget']]()

            # Create, initialize, and bind the toolkit widget. We swap 
            # the order of the pipes on purpose, which provides the 
            # other end of the pipe to the widget as required.
            # XXX we may want to delay some of this initialization
            widget = widget_cls(parent, uuid, recv_pipe, send_pipe)
            widget.create()
            widget.initialize(info_dct['attrs'])
            widget.bind()
            children = info_dct['children']
            info_stack.extend(izip_longest(children, [], fillvalue=widget))

            # Store a reference to the root widget to prevent things 
            # from being garbage collected
            if parent is None:
                self._root = widget

        # Temparary hack to initialize layout
        stack = [self._root]
        while stack:
            child = stack.pop()
            child.initialize_layout()
            stack.extend(child.children)


def local_id_gen(stem):
    """ An identifier generator used by the QtLocalApplication to 
    generate unique identifiers for messaging.

    Parameters
    ----------
    stem : str
        A string stem to prepend to a incrementing integer value.

    """
    counter = count()
    str_ = str
    while True:
        yield stem % str_(counter.next())

       
class QtLocalApplication(AsyncApplication):
    """ An Enaml AsyncApplication which executes in the local process
    and uses Qt to create the client widgets.

    """
    def __init__(self):
        self._qapp = QApplication([])
        self._target_id_gen = local_id_gen('w')
        op_id_gen = local_id_gen('op')
        self._server_pipe = QtLocalPipe(op_id_gen)
        self._client_pipe = QtLocalPipe(op_id_gen)

    #--------------------------------------------------------------------------
    # AsyncApplication Interface
    #--------------------------------------------------------------------------
    def register(self, messenger):
        """ Register a messenger with the application.

        """
        target_id = self._target_id_gen.next()
        return (target_id, self._server_pipe, self._client_pipe)

    def builder(self):
        return QtLocalClientBuilder()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def run(self):
        app = self._qapp
        if not getattr(app, '_in_event_loop', False):
            app._in_event_loop = True
            app.exec_()
            app._in_event_loop = False

