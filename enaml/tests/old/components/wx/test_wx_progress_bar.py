#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_test_assistant import WXTestAssistant, skip_nonwindows
from .. import progress_bar


@skip_nonwindows
class TestWXProgressBar(WXTestAssistant, progress_bar.TestProgressBar):
    """ WXProgressBar tests.

    .. note:: The wx test uses the extended signature because the range and
        value of the progress bar is related to the minimum attribute.

    """

    def get_value(self, component, widget):
        """  Get the toolkits widget's active value.

        """
        return widget.GetValue() + component.minimum

    def get_minimum(self, component, widget):
        """  Get the toolkits widget's maximum value attribute.

        .. note:: The minimum value is maintained only in the component

        """
        return component.minimum

    def get_maximum(self, component, widget):
        """ Get the toolkits widget's minimum value attribute.

        """
        return widget.GetRange() - component.minimum
