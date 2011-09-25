#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

import wx

from ..common.label import TestLabel


class TestWxLabel(TestLabel, unittest.TestCase):
    """ WXLabel tests. """
    
    def get_text(self, widget):
        """ Get a label's text.
        
        """
        return widget.GetLabel()
