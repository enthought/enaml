#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

from ..common.label import TestLabel

class TestQtLabel(TestLabel, unittest.TestCase):
    """ QtLabel tests. """
    
    def get_text(self, widget):
        """ Get a label's text.
        
        """
        return widget.text()
