#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from uuid import uuid4

from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_html import QtHtml
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtHtml(object):
    """ Unit tests for the QtHtml

    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
            
    def setUp(self):
        """ Set up the widget for testing

        """
        self.html = QtHtml(None, uuid4().hex, QtLocalPipe(uuid4))
        self.html.create()

    def test_set_source(self):
        """ Test the QtHtml's set_source command

        """
        source = "<html><p>hello</p></html>"
        self.html.recv_message({'action':'set-source', 'source':source})
        # Qt wraps the html with a bunch of metadata and extra tags,
        # so we compare the plain text
        assert self.html.widget.toPlainText() == 'hello'
