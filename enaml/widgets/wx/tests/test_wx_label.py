#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

import unittest
import sys
from enaml.util.test_utils import EnamlTestCase

class testWXLabel(EnamlTestCase):
    """ Testsuite for WXLabel
    """

    enaml = \
"""
Window:
    Panel:
        VGroup:
            Label:
                name = 'tested_widget'
                text = 'test label'
"""

    def test_initial_contents(self):
        """Check the text value of the WXLabel"""

        enaml_widget = self.get_widget('tested_widget')
        widget = enaml_widget.toolkit_widget()

        self.assertEqual('test label', widget.GetLabel(),
            "The widget's label should be {0}".format('test label'))
        self.assertEqual(enaml_widget.text, widget.GetLabel(),
            "The text attribute does not agree with the widget's label")

    @unittest.skipIf(sys.platform.startswith("win"), "Coredump in Windows")
    def test_label_change(self):
        """Test changing the label of a WXLabel"""

        enaml_widget = self.get_widget('tested_widget')
        widget = enaml_widget.toolkit_widget()

        new_label = 'new_label'
        enaml_widget.text = new_label

        self.assertEqual(new_label, widget.GetLabel(),
            "The widget's label should be {0}".format(new_label))
        self.assertEqual(enaml_widget.text, widget.GetLabel(),
            "The text attribute does not agree with the widget's label")


if __name__ == '__main__':
    import unittest
    unittest.main()
