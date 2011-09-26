#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ..common import label

class TestWxLabel(label.TestLabel):
    """ WXLabel tests. """


    def get_text(self, widget):
        """ Get a label's text.
        
        """
        return widget.GetLabel()
