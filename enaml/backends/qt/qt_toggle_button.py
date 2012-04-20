#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtCore, QtGui
from .qt_toggle_control import QtToggleControl

from ...components.toggle_button import AbstractTkToggleButton


class QtToggleButton(QtToggleControl, AbstractTkToggleButton):
    """ A Qt implementation of ToggleButton.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QPushButton control which has the 
        'checkable' property set to True.

        """
        self.widget = QtGui.QPushButton(parent)
        # The QPushButton is not toggleable until it is 'setCheckable'. 
        # It must be toggleable before 'QtToggleControl.initialize' is 
        # called, so we do that here.
        self.widget.setCheckable(True)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtToggleButton, self).initialize()
        self.set_icon(self.shell_obj.icon)
        self.set_icon_size(self.shell_obj.icon_size)
        
    def bind(self):
        """ Binds the event handlers for the toggle button.

        """
        super(QtToggleButton, self).bind()
        widget = self.widget
        widget.toggled.connect(self.on_toggled)
        widget.pressed.connect(self.on_pressed)
        widget.released.connect(self.on_released)
        
    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_icon_changed(self, icon):
        """ The change handler for the 'icon' attribute.

        """
        self.set_icon(icon)
        # If the icon of the button changes, the size hint has likely
        # changed and the layout system needs to be informed.
        self.shell_obj.size_hint_updated()

    def shell_icon_size_changed(self, icon_size):
        """ The change handler for the 'icon_size' attribute.

        """
        self.set_icon_size(icon_size)
        # If the icon of the button changes, the size hint has likely
        # changed and the layout system needs to be informed.
        self.shell_obj.size_hint_updated()

    def set_icon(self, icon):
        """ Sets the icon on the button control.

        """
        if icon is None:
            qicon = QtGui.QIcon()
        else:
            qicon = icon.as_QIcon()
        self.widget.setIcon(qicon)

    def set_icon_size(self, icon_size):
        """ Sets the icon size on the button control.

        """
        if (icon_size is not None and 
            icon_size.width > 0 and 
            icon_size.height > 0):
            self.widget.setIconSize(QtCore.QSize(*icon_size))

