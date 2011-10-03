#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .. import html
from enaml.toolkit import wx_toolkit


class TestWxHtml(html.TestHtml):
    """ WXHtml tests. """

    toolkit = wx_toolkit()

    def get_source(self, widget):
        """ Get the source of an Html widget.
        
        """
        return widget.ToText()
        
