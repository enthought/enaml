#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase, required_method


class TestHtml(EnamlTestCase):
    """ Logic for testing Html widgets.

    The toolkits return HTML as plain text, so we do not compare formatting.
    Tooklit testcases need to provide the following methods

    Abstract Methods
    ----------------
    get_source(self, widget)
        Get the source of an Html widget.

    """
    text = 'That is a bold claim.'

    def setUp(self):
        """ Set up before the Html tests.

        """
        enaml_source = """
enamldef MainView(MainWindow):
    Html:
        name = 'html'
        source = '<b>{0}</b>'
""".format(self.text)

        self.view = self.parse_and_create(enaml_source)
        self.component = self.component_by_name(self.view, 'html')
        self.widget = self.component.toolkit_widget

    def test_initial_source(self):
        """ Test the initial source of an Html widget.

        """
        widget_source = self.get_source(self.widget)
        self.assertEqual(widget_source, self.text)

    def test_source_changed(self):
        """ Change the source of an Html widget.

        """
        new_text = 'Underlined'
        new_source = '<u>{0}</u>'.format(new_text)
        self.component.source = new_source
        widget_source = self.get_source(self.widget)
        self.assertEqual(widget_source, new_text)

    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @required_method
    def get_source(self, widget):
        """ Get the source of an Html widget.

        """
        pass

