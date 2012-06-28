#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from uuid import uuid4

from enaml.qt.qt.QtGui import QApplication, QLineEdit, QIntValidator
from enaml.qt.qt_enaml_validator import QtEnamlValidator
from enaml.qt.qt_field import QtField
from enaml.qt.qt_local_pipe import QtLocalPipe

class TestQtField(object):
    """ Unit tests for the QtField

    """
    def __init__(self):
        """ Create an application instance so that widgets can be created

        """
        if not QApplication.instance():
            self.app = QApplication([])
    
    def setUp(self):
        """ Set up the widget for testing

        """
        self.field = QtField(None, uuid4().hex, QtLocalPipe(),
                             QtLocalPipe())
        self.field.create()

    def test_set_max_length(self):
        """ Test the QtField's set_max_length command

        """
        max_length = 20
        self.field.recv('set_max_length', {'value':max_length})
        assert self.field.widget.maxLength() == max_length

    def test_set_password_mode(self):
        """ Test the QtField's set_password_mode command

        """
        password_mode = QLineEdit.Password
        self.field.recv('set_password_mode', {'value':'password'})
        assert self.field.widget.echoMode() == password_mode

    def test_set_placeholder_text(self):
        """ Test the QtField's set_placeholder_text command

        """
        p_text = "Placeholder text"
        self.field.recv('set_placeholder_text', {'value':p_text})
        assert self.field.widget.placeholderText() == p_text

    def test_set_read_only(self):
        """ Test the QtField's set_read_only command

        """
        self.field.recv('set_read_only', {'value':True})
        assert self.field.widget.isReadOnly() == True

    def test_set_text(self):
        """ Test the QtField's set_text command

        """
        text = "Test"
        self.field.recv('set_text', {'text':text})
        assert self.field.widget.text() == text

    def test_set_validator(self):
        """ Test the QtField's set_validator command

        """
        validator = QtEnamlValidator(QIntValidator())
        self.field.recv('set_validator', {'value':validator})
        # a new instance of the validator is created when it is set,
        # so the best we can do is check that the types are the same,
        # as the default Qt validator will not be of type QtEnamlValidator
        assert type(self.field.widget.validator()) == type(validator)
