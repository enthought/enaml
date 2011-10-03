#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import abc

from .enaml_test_case import EnamlTestCase


class TestHtml(EnamlTestCase):
    """ Logic for testing Html widgets.

    The toolkits return HTML as plain text, so we do not compare formatting.
    Tooklit testcases need to provide the following methods

    Abstract Methods
    ----------------
    get_source(self, widget)
        Get the source of an Html widget.

    """

    __metaclass__  = abc.ABCMeta

    text = 'That is a bold claim.'

    enaml = """
Window:
    Panel:
        VGroup:
            Html html:
                source = '<b>{0}</b>'
""".format(text)

    def setUp(self):
        """ Set up before the Html tests.

        """
        super(TestHtml, self).setUp()
        component = self.widget_by_id('html')
        self.widget = component.toolkit_widget()
        self.component = component

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
    # absrtact methods
    #--------------------------------------------------------------------------

    @abc.abstractmethod
    def get_source(self, widget):
        """ Get the source of an Html widget.

        """
        return NotImplemented
