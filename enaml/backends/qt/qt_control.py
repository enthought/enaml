#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from .qt.QtCore import Qt
from .qt_constraints_widget import QtConstraintsWidget

from ...components.control import AbstractTkControl


class QtControl(QtConstraintsWidget, AbstractTkControl):
    """ A Qt4 implementation of Control.

    """
    _default_focus_attr = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def initialize(self):
        """ Initializes the attributes of the underlying control.

        """
        super(QtControl, self).initialize()
        shell = self.shell_obj
        self.set_show_focus_rect(shell.show_focus_rect)

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def shell_show_focus_rect_changed(self, show):
        """ The change handler for the 'show_focus_rect' attribute on 
        the shell object.

        """
        self.set_show_focus_rect(show)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_show_focus_rect(self, show):
        """ Sets whether or not to show the focus rectangle around
        a widget. This currently only applies to OSX.

        """
        if sys.platform == 'darwin':
            attr = Qt.WA_MacShowFocusRect
            if show == 'default':
                if self._default_focus_attr is not None:
                    self.widget.setAttribute(attr, self._default_focus_attr)
            else:
                if self._default_focus_attr is None:
                    self._default_focus_attr = self.widget.testAttribute(attr)
                self.widget.setAttribute(attr, show)
                
