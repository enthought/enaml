#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtCore, QtGui
from .qt_control import QtControl

from ...components.push_button import AbstractTkPushButton


class QtPushButton(QtControl, AbstractTkPushButton):
    """ A Qt implementation of PushButton.

    """
    
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QPushButton control.

        """
        self.widget = QtGui.QPushButton(parent)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtPushButton, self).initialize()
        self.set_text(self.shell_obj.text)
        self.set_icon(self.shell_obj.icon)
        self.set_icon_size(self.shell_obj.icon_size)

    def bind(self):
        """ Connects the event handlers for the push button.

        """
        super(QtPushButton, self).bind()
        widget = self.widget
        widget.clicked.connect(self.on_clicked)
        widget.pressed.connect(self.on_pressed)
        widget.released.connect(self.on_released)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_text_changed(self, text):
        """ The change handler for the 'text' attribute.

        """
        self.set_text(text)
        # If the text of the button changes, the size hint has likely
        # change and the layout system needs to be informed.
        self.shell_obj.size_hint_updated()

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
        # If the icon size of the button changes, the size hint has likely
        # changed and the layout system needs to be informed.
        self.shell_obj.size_hint_updated()

    def on_clicked(self):
        """ The event handler for the button's clicked event.

        """
        shell = self.shell_obj
        shell._down = False
        shell.clicked()

    def on_pressed(self):
        """ The event handlers for the button's pressed event.

        """
        shell = self.shell_obj
        shell._down = True
        shell.pressed()

    def on_released(self):
        """ The event handler for the button's released event.

        """
        shell = self.shell_obj
        if shell._down:
            shell._down = False
            shell.released()

    def set_text(self, text):
        """ Sets the text on the button control.

        """
        self.widget.setText(text)

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
        if icon_size is not None and (icon_size.width > 0 
                                      and icon_size.height > 0):
            self.widget.setIconSize(QtCore.QSize(*icon_size))

