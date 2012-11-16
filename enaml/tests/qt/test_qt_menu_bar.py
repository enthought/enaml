#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from uuid import uuid4

from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_menu_bar import QtMenuBar
from enaml.qt.qt_menu import QtMenu
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtMenuBar(object):
    """ Unit tests for the QtMenuBar

    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
    
    def setUp(self):
        """ Set up the widget for testing

        """
        self.menu_bar = QtMenuBar(None, uuid4().hex, QtLocalPipe(uuid4))
        self.menu_bar.create()

    def test_set_menus(self):
        """ Test the QtMenuBar's set_menus command

        """
        menu1 = QtMenu(self.menu_bar, uuid4().hex, QtLocalPipe(uuid4))
	menu1.create()
        menu1.set_title('test1')
	
        menu2 = QtMenu(self.menu_bar, uuid4().hex, QtLocalPipe(uuid4))
	menu2.create()
        menu2.set_title('test2')

        menus = [menu1, menu2]

	self.menu_bar.recv_message({'action':'set-menus', 'menus':menus})
        assert self.menu_bar.children == menus
