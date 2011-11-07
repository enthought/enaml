#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import TraitError

from .enaml_test_case import EnamlTestCase, required_method

class TestWindow(EnamlTestCase):
    """ Logic for testing Windows.

    """

    def setUp(self):
        """ Set up Window tests.

        """

        enaml_source = """
defn MainWindow():
    Window -> window:
        title = 'foo'
"""

        self.view = self.parse_and_create(enaml_source)
        self.component = self.component_by_name(self.view, 'window')
        self.widget = self.component.toolkit_widget

    def test_initial_title(self):
        """ Test the initial title of a Window.

        """
        self.assertEnamlInSync(self.component, 'title', 'foo')

    def test_initial_modality(self):
        """ Test the initial modality of a Window.

        """
        self.assertEnamlInSync(self.component, 'modality', 'non_modal')

    def test_title_changed(self):
        """ Change the title of the Window.

        """
        self.component.title = 'bar'
        self.assertEnamlInSync(self.component, 'title', 'bar')

    def test_modality_changed(self):
        """ Change the modality of the Window.

        """
        self.component.modality = 'window_modal'
        self.assertEnamlInSync(self.component, 'modality', 'window_modal')
        self.component.modality = 'application_modal'
        self.assertEnamlInSync(self.component, 'modality', 'application_modal')
        self.component.modality = 'non_modal'
        self.assertEnamlInSync(self.component, 'modality', 'non_modal')
        self.assertRaises(TraitError, self.component.trait_set, modality='app_modal')
        self.assertEnamlInSync(self.component, 'modality', 'non_modal')
        self.assertRaises(TraitError, self.component.trait_set, modality='win_modal')
        self.assertEnamlInSync(self.component, 'modality', 'non_modal')


    #--------------------------------------------------------------------------
    # absrtact methods
    #--------------------------------------------------------------------------


    @required_method
    def get_title(self, widget):
        """ Returns the title from the toolkit widget.

        """
        pass

    @required_method
    def get_modality(self, widget):
        """ Returns the modality from the toolkit widget.

        """
        pass

