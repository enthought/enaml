#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase, required_method


class TestLessLess(EnamlTestCase):
    """ Generic testcases for enaml the LessLess operator.

    These testcases test the basic functionality of widgets interacting
    with each other.

    To run these tests for a specific back-end it is required to have
    a functional implementation of the following wigdets:
        - Window
        - CheckBox
        - Label

    Abstract Methods
    ----------------
    get_text(widget)
        Returns the text from the tookit widget of a Label.

    get_checked(widget)
        Return the checked status of a CheckBox.

    """
    def setUp(self):
        enaml_source = """
enamldef MainView(MainWindow):
    Container:
        Label:
            name = 'lb'
            text << 'CheckBox is {0}'.format(cb.checked)
        CheckBox:
            id: cb
            name = 'cb'
            text = 'Should be checked'
            checked = True
"""
        self.view = self.parse_and_create(enaml_source)
        self.label = self.component_by_name(self.view, 'lb')
        self.check_box = self.component_by_name(self.view, 'cb')
        self.label_widget = self.label.toolkit_widget
        self.check_box_widget = self.check_box.toolkit_widget

    def test_lessless_init(self):
        """ Test the value after initialization

        """
        label = self.label
        check_box = self.check_box
        self.assertEnamlInSync(check_box, 'checked', True)
        self.assertEnamlInSync(label, 'text', 'CheckBox is True')

    def test_lessless_update(self):
        """ Test the value after initialization

        """
        label = self.label
        check_box = self.check_box
        check_box.checked = False
        self.assertEnamlInSync(label, 'text', 'CheckBox is False')
        self.assertEnamlInSync(check_box, 'checked', False)

    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @required_method
    def get_text(self, widget):
        """ Returns the label text from the tookit widget of Label.

        """
        pass

    @required_method
    def get_checked(self, widget):
        """ Returns the label text from the tookit widget of CheckBox.

        """
        pass

