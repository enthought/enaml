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

    def setUp(self):
        """ Set up label tests.

        """

        enaml_source = """
enamldef MainView(MainWindow):
    Label:
        name = 'label'
        text = 'foo'
"""

        self.view = self.parse_and_create(enaml_source)
        self.component = self.component_by_name(self.view, 'label')
        self.widget = self.component.toolkit_widget

    def test_initial_text(self):
        """ Test the initial text of a label.

        """
        self.assertEnamlInSync(self.component, 'text', 'foo')

    def test_text_changed(self):
        """ Change the text of the label.

        """

        self.component.text = 'bar'
        self.assertEnamlInSync(self.component, 'text', 'bar')

    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @required_method
    def get_text(self, widget):
        """ Returns the label text from the tookit widget

        """
        pass

