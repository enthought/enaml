#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from itertools import izip_longest

from enaml.application import Application

from .mock_pipe import MockPipe
from .mock_widget import MockWidget


class MockBuilder(object):
    """ A builder that generates a client-side UI tree.

    """
    def __init__(self):
        self._root = None

    @property
    def root(self):
        return self._root

    def build(self, info):
        info_stack = [(info, None)]
        while info_stack:
            info_dct, parent = info_stack.pop()
            send_pipe = info_dct['send_pipe']
            recv_pipe = info_dct['recv_pipe']
            widget_cls = MockWidget
            # Cross the pipes when hooking the MockWidget up to the server widget
            widget = widget_cls(info_dct['widget'], parent, recv_pipe, send_pipe)
            widget.initialize(info_dct['attrs'])
            children = info_dct['children']
            info_stack.extend(izip_longest(children, [], fillvalue=widget))

            # Store a reference to the root widget to prevent things 
            # from being garbage collected
            if parent is None:
                self._root = widget


class MockApplication(Application):
    """ A mock application for testing server widget components.

    """
    def __init__(self):
        self._builder = None

    #--------------------------------------------------------------------------
    # Abstract API implementation
    #--------------------------------------------------------------------------
    def register(self, messenger):
        return (MockPipe(), MockPipe())

    def builder(self):
        if self._builder is None:
            self._builder = MockBuilder()
        return self._builder

