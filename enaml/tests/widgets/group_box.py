#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import TraitError
from .enaml_test_case import EnamlTestCase, required_method


class TestGroupBox(EnamlTestCase):
    """ Logic for testing labels.

    Tooklit testcases need to provide the following methods:

    Abstract Methods
    ----------------
    get_title
        Returns the group title from the tookit widget

    get_flat
        Returns the flat border style from the tookit widget

    get_title_align
        Returns the title align style from the tookit widget

    Notes
    -----
    All the provided methods need to support the extented signature
    <method>(component, widget).

    """

    def setUp(self):
        """ Set up label tests.

        """

        enaml_source = """
defn MainWindow():
    Window -> win:
        contrains = [horizontal(left, gb, right), vertical(top, gb, bottom),
                    vertical(label1, label2), align_left(label1, label2)]
        GroupBox -> gb:
            title = 'MyGroup'
            flat = True
            title_align = 'center'
            Label -> label1:
                text = 'foofoofoofoofoofoofoofoofoofoofoofoo'
            Label -> label2:
                text = 'barbarbarbarbarbarbarbarbarbar'
"""
        self.view = self.parse_and_create(enaml_source)
        self.component = self.component_by_name(self.view, 'gb')
        self.widget = self.component.toolkit_widget

    def test_initialization(self):
        """ Test initialization

        Test that the atrributes of the GroupBox have the
        correct values and these values are insync with the information
        in the toolkit widget.

        """
        component = self.component
        self.assertEnamlInSync(component, 'title', 'MyGroup')
        self.assertEnamlInSync(component, 'flat', True)
        self.assertEnamlInSync(component, 'title_align', 'center')

    def test_title_changed(self):
        """ Change the title text of the GroupBox.

        """
        component = self.component
        component.title = "New title"
        self.assertEnamlInSync(component, 'title', 'New title')

    def test_flat_style_changed(self):
        """ Change the flat style border of the GroupBox.

        """
        component = self.component
        component.flat = False
        self.assertEnamlInSync(component, 'flat', False)

    def test_title_align_changed(self):
        """ Change the title alignment.

        """
        component = self.component
        component.title_align = 'right'
        self.assertEnamlInSync(component, 'title_align', 'right')
        component.title_align = 'left'
        self.assertEnamlInSync(component, 'title_align', 'left')
        component.title_align = 'center'
        self.assertEnamlInSync(component, 'title_align', 'center')

    def test_invalid_alignment(self):
        """ Change the title alignment to an invalid value.

        """
        component = self.component
        with self.assertRaises(TraitError):
            component.title_align = 'almost center'
        self.assertEnamlInSync(component, 'title_align', 'center')

    #--------------------------------------------------------------------------
    # absrtact methods
    #--------------------------------------------------------------------------
    @required_method
    def get_title(self, widget):
        """ Returns the title text from the tookit widget

        """
        pass

    @required_method
    def get_flat(self, widget):
        """ Returns the flat style status from the tookit widget

        """
        pass

    @required_method
    def get_title_align(self, widget):
        """ Returns the title aligment in the tookit widget

        """
        pass
