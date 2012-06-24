#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from itertools import izip_longest

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
            send_pipe = info_dct['send_pipe']
            recv_pipe = info_dct['recv_pipe']
            widget_cls = CLIENTS[info_dct['widget']]()

            # Create, initialize, and bind the toolkit widget. We swap 
            # the order of the pipes on purpose, which provides the 
            # other end of the pipe to the widget as required.
            # XXX we may want to delay some of this initialization
            widget = widget_cls(parent, recv_pipe, send_pipe)
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


class QtLocalApplication(AsyncApplication):
    """ An Enaml AsyncApplication which executes in the local process
    and uses Qt to create the client widgets.

    """
    def __init__(self):
        self._qapp = QApplication([])

    #--------------------------------------------------------------------------
    # Abstract API implementation
    #--------------------------------------------------------------------------
    def register(self, messenger):
        return (QtLocalPipe(), QtLocalPipe())

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

