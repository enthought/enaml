#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_constraints_widget import WXConstraintsWidget

from ...components.control import AbstractTkControl


class WXControl(WXConstraintsWidget, AbstractTkControl):
    """ A Wx implementation of the base Control.

    """
    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def shell_show_focus_rect_changed(self, show):
        """ The change handler for the 'show_focus_rect' attribute on 
        the shell object.

        """
        # This currently has not effect on Wx.
        pass

