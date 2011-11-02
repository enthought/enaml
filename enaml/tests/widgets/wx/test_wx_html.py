#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_test_assistant import WXTestAssistant, skip_nonwindows
from .. import html


@skip_nonwindows
class TestWxHtml(WXTestAssistant, html.TestHtml):
    """ WXHtml tests. """

    def get_source(self, widget):
        """ Get the source of an Html widget.

        """
        return widget.ToText()

