#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ..common import label
from enaml.toolkit import wx_toolkit

class TestWxLabel(label.TestLabel):
    """ WXLabel tests. """

    toolkit = wx_toolkit()

    def get_text(self, widget):
        """ Get a label's text.
        
        """
        return widget.GetLabel()
