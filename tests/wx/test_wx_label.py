#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from . import send_wx_event

from ..common.label import TestLabel


class TestWxLabel(TestLabel):
    """ WXLabel tests. """
    
    def test_initial_text(self):
        """ Test the initial text of a label.
        
        """
        self.check_text(self.text)
    
    def test_text_changed(self):
        """ Change the text of the label.
        
        """
        self.component.text = 'bar'
        widget_text = self.widget.GetLabel()
        self.check_text(widget_text)
