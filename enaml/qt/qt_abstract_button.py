#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from base64 import b64decode

from .qt.QtCore import QSize
from .qt_constraints_widget import QtConstraintsWidget
from .qt_icon import QtIcon


class QtAbstractButton(QtConstraintsWidget):
    """ A Qt4 implementation of the Enaml AbstractButton class.

    This class can serve as a base class for widgets that implement 
    button behavior such as CheckBox, RadioButton and PushButtons. 
    It is not meant to be used directly.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self):
        """ The create method must be implemented by subclasses to 
        create an instance of QAbstractButton.

        """
        raise NotImplementedError

    def initialize(self, attrs):
        """ Initialize the attribute of the underlying Qt widget.

        """
        super(QtAbstractButton, self).initialize(attrs)
        self.set_checkable(attrs['checkable'])
        self.set_checked(attrs['checked'])
        self.set_text(attrs['text'])
        self.set_icon(attrs['icon'])
        self.set_icon_size(attrs['icon_size'])
        self.widget.clicked.connect(self.on_clicked)
        self.widget.toggled.connect(self.on_toggled)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_checked(self, payload):
        """ Handle the 'set-checked' action from the Enaml widget.

        """
        self.set_checked(payload['checked'])

    def on_message_set_text(self, payload):
        """ Handle the 'set-text' message from the Enaml widget.

        """
        self.set_text(payload['text'])
        # Trigger a relayout since the size hint likely changed

    def on_message_set_icon(self, payload):
        """ Handle the 'set-icon' message from the Enaml widget.

        """
        self.set_icon(payload['icon'])

    def on_message_set_icon_size(self, payload):
        """ Handle the 'set-icon_size' message from the Enaml widget.

        """
        self.set_icon_size(payload['icon_size'])

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_clicked(self):
        """ The event handler fo the clicked event.

        """
        payload = {
            'action': 'event-clicked', 'checked': self.widget.isChecked(),
        }
        self.send_message(payload)

    def on_toggled(self):
        """ The event handler for the toggled event.

        """
        payload = {
            'action': 'event-toggled', 'checked': self.widget.isChecked(),
        }
        self.send_message(payload)

    #--------------------------------------------------------------------------
    # Widget update methods
    #--------------------------------------------------------------------------
    def set_checkable(self, checkable):
        """ Sets whether or not the widget is checkable.

        """
        self.widget.setCheckable(checkable)

    def set_checked(self, checked):
        """ Sets the widget's checked state with the provided value.

        """
        widget = self.widget
        # This handles the case where, by default, Qt will not allow
        # all of the radio buttons in a group to be disabled. By 
        # temporarily turning off auto-exclusivity, we are able to
        # handle that case.
        if not checked and widget.isChecked() and widget.autoExclusive():
            widget.setAutoExclusive(False)
            widget.setChecked(checked)
            widget.setAutoExclusive(True)
        else:
            widget.setChecked(checked)

    def set_text(self, text):
        """ Sets the widget's text with the provided value.

        """
        self.widget.setText(text)

    def set_icon(self, icon):
        """ Sets the widget's icon to the provided image

        """
        return
        dec_data = b64decode(icon)
        self._icon = QtIcon(dec_data)
        self.widget.setIcon(self._icon.as_QIcon())

    def set_icon_size(self, icon_size):
        """ Sets the widget's icon size to the provided tuple

        """
        return
        self.widget.setIconSize(QSize(*icon_size))

