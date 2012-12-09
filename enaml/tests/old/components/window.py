#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase, required_method


class TestWindow(EnamlTestCase):
    """ Logic for testing Windows.

    """
    def setUp(self):
        """ Set up Window tests.

        """

        enaml_source = """
enamldef MainView(MainWindow):
    name = 'window'
    title = 'foo'
"""

        self.view = self.parse_and_create(enaml_source)
        self.component = self.component_by_name(self.view, 'window')
        self.widget = self.component.toolkit_widget

    def test_initial_title(self):
        """ Test the initial title of a Window.

        """
        self.assertEnamlInSync(self.component, 'title', 'foo')

    def test_title_changed(self):
        """ Change the title of the Window.

        """
        self.component.title = 'bar'
        self.assertEnamlInSync(self.component, 'title', 'bar')

    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @required_method
    def get_title(self, widget):
        """ Returns the title from the toolkit widget.

        """
        pass

