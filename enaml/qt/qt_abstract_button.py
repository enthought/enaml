#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_constraints_widget import QtConstraintsWidget


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

    def initialize(self, init_attrs):
        """ Initialize the attribute of the underlying Qt widget.

        """
        super(QtAbstractButton, self).initialize(init_attrs)
        self.set_checkable(init_attrs['checkable'])
        self.set_checked(init_attrs['checked'])
        self.set_text(init_attrs['text']) 

    def bind(self):
        """ Bind the signal handlers for the underlying control.

        """
        super(QtAbstractButton, self).bind()
        widget = self.widget
        widget.pressed.connect(self.on_pressed)
        widget.released.connect(self.on_released)
        widget.clicked.connect(self.on_clicked)
        widget.toggled.connect(self.on_toggled)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_checkable(self, ctxt):
        """ Handle the 'set_checkable' message from the Enaml widget.

        """
        self.set_checkable(ctxt['checkable'])

    def receive_set_checked(self, ctxt):
        """ Handle the 'set_checked' message from the Enaml widget.

        """
        self.set_checked(ctxt['checked'])

    def receive_set_text(self, ctxt):
        """ Handle the 'set_text' message from the Enaml widget.

        """
        self.set_text(ctxt['text'])
        # Trigger a relayout since the size hint likely changed

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_pressed(self):
        """ The event handler for the pressed event.

        """
        self.send({'action':'pressed'})

    def on_released(self):
        """ The event handler for the released event.

        """
        self.send({'action':'released'})

    def on_clicked(self):
        """ The event handler fo the clicked event.

        """
        self.send({'action':'clicked','checked': self.widget.isChecked()})

    def on_toggled(self):
        """ The event handler for the toggled event.

        """
        self.send({'action':'toggled','checked': self.widget.isChecked()})

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

