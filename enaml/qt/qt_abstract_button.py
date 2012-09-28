#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import QSize
from .qt_constraints_widget import QtConstraintsWidget
#from .qt_image import QtImage


class QtAbstractButton(QtConstraintsWidget):
    """ A Qt implementation of the Enaml AbstractButton class.

    This class can serve as a base class for widgets that implement 
    button behavior such as CheckBox, RadioButton and PushButtons. 
    It is not meant to be used directly.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ This method must be implemented by subclasses to create 
        the proper button widget.

        """
        raise NotImplementedError

    def create(self, tree):
        """ Create and initialize the abstract button widget.

        """
        super(QtAbstractButton, self).create(tree)
        self.set_checkable(tree['checkable'])
        self.set_checked(tree['checked'])
        self.set_text(tree['text'])
        #self.set_icon(tree['icon'])
        self.set_icon_size(tree['icon_size'])
        widget = self.widget()
        widget.clicked.connect(self.on_clicked)
        widget.toggled.connect(self.on_toggled)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_clicked(self):
        """ The signal handler for the 'clicked' signal.

        """
        content = {'checked': self.widget().isChecked()}
        self.send_action('clicked', content)

    def on_toggled(self):
        """ The signal handler for the 'toggled' signal.

        """
        content = {'checked': self.widget().isChecked()}
        self.send_action('toggled', content)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_checked(self, content):
        """ Handle the 'set_checked' action from the Enaml widget.

        """
        self.set_checked(content['checked'])

    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        item = self.widget_item()
        old_hint = item.sizeHint()
        self.set_text(content['text'])
        new_hint = item.sizeHint()
        if old_hint != new_hint:
            self.size_hint_updated()

    def on_action_set_icon_size(self, content):
        """ Handle the 'set_icon_size' action from the Enaml widget.

        """
        self.set_icon_size(content['icon_size'])

    #--------------------------------------------------------------------------
    # Widget update methods
    #--------------------------------------------------------------------------
    def set_checkable(self, checkable):
        """ Sets whether or not the widget is checkable.

        """
        self.widget().setCheckable(checkable)

    def set_checked(self, checked):
        """ Sets the widget's checked state with the provided value.

        """
        widget = self.widget()
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
        self.widget().setText(text)

    def set_icon(self, icon):
        """ Sets the widget's icon to the provided image.

        """
        return
        #self._icon = QtImage(icon)
        #self.widget.setIcon(self._icon.as_QIcon())

    def set_icon_size(self, icon_size):
        """ Sets the widget's icon size to the provided size.

        """
        self.widget().setIconSize(QSize(*icon_size))

