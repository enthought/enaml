#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase, required_method


class TestLabel(EnamlTestCase):
    """ Logic for testing labels.

    Tooklit testcases need to provide the following methods

    Abstract Methods
    ----------------
    get_text()
        Returns the label text from the tookit widget

    """

    enaml = """
Window:
    Panel:
        VGroup:
            Label label:
                text = 'foo'
"""

    def setUp(self):
        """ Set up label tests.

        """
        super(TestLabel, self).setUp()
        component = self.widget_by_id('label')
        self.widget = component.toolkit_widget()
        self.component = component

    def test_initial_text(self):
        """ Test the initial text of a label.

        """
        self.assertEqual(self.component.text, self.get_text(self.widget))

    def test_text_changed(self):
        """ Change the text of the label.

        """

        self.component.text = 'bar'
        widget_text = self.get_text(self.widget)
        self.assertEqual(self.component.text, widget_text)

    #--------------------------------------------------------------------------
    # absrtact methods
    #--------------------------------------------------------------------------


    @required_method
    def get_text(self, widget):
        """ Returns the label text from the tookit widget

        """
        pass
