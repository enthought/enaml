#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_component import QtComponent

from ..action import AbstractTkAction


class QtAction(QtComponent, AbstractTkAction):
    """ A Qt4 implementation of Action.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QAction object.

        """
        self.widget = QtGui.QAction(parent)

    def initialize(self):
        """ Initializes the underlying QAction object.

        """
        super(QtAction, self).initialize()
        shell = self.shell_obj
        self.set_text(shell.text)
        self.set_checkable(shell.checkable)
        self.set_checked(shell.checked)
        self.set_status_tip(shell.status_tip)
        self.set_tool_tip(shell.tool_tip)
        self.set_description(shell.description)
        self.set_separator(shell.separator)
        
    def bind(self):
        """ Binds the event handlers for the underlying QAction object.

        """
        super(QtAction, self).bind()
        widget = self.widget
        widget.triggered.connect(self.on_triggered)
        widget.hovered.connect(self.on_hovered)
        widget.toggled.connect(self.on_toggled)

    #--------------------------------------------------------------------------
    # Teardown Methods 
    #--------------------------------------------------------------------------
    def destroy(self):
        """ Overridden parent class method which properly disposes of 
        the underlying QAction object.

        """
        # A QAction does not inherit QWidget and so doesn't have a 
        # destroy() method. So, we just unparent the object and lose
        # the reference.
        self.widget.setParent(None)
        self.widget = None

    #--------------------------------------------------------------------------
    # Change Handlers 
    #--------------------------------------------------------------------------
    def shell_text_changed(self, text):
        """ The change handler for the 'text' attribute on the shell
        object.

        """
        self.set_text(text)
    
    def shell_checkable_changed(self, checkable):
        """ The change handler for the 'checkable' attribute on the 
        shell object.

        """
        self.set_checkable(checkable)
    
    def shell_checked_changed(self, checked):
        """ The change handler for the 'checked' attribute on the
        shell object.

        """
        self.set_checked(checked)

    def shell_status_tip_changed(self, status_tip):
        """ The change handler for the 'status_tip' attribute on the 
        shell object.

        """
        self.set_status_tip(status_tip)
    
    def shell_tool_tip_changed(self, tool_tip):
        """ The change handler for the 'tool_tip' attribute on the 
        shell object.

        """
        self.set_tool_tip(tool_tip)
    
    def shell_description_changed(self, description):
        """ The change handler for the 'description' attribute on the 
        shell object.

        """
        self.set_description(description)

    def shell_separator_changed(self, separator):
        """ The change handler for the 'separator' attribute on the
        shell object.

        """
        self.set_separator(separator)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_triggered(self):
        """ A signal handler for the 'triggered' signal of the QAction.

        """
        self.shell_obj.triggered()

    def on_hovered(self):
        """ A signal handler for the 'hovered' signal of the QAction.

        """
        self.shell_obj.hovered()

    def on_toggled(self):
        """ A signal handler for the 'toggled' signal of the QAction.

        """
        shell = self.shell_obj
        shell.checked = self.widget.isChecked()
        shell.toggled()

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Sets the text of the action.

        """
        self.widget.setText(text)

    def set_checkable(self, checkable):
        """ Sets whether or not the action is checkable.

        """
        self.widget.setCheckable(checkable)
    
    def set_checked(self, checked):
        """ Sets whether or not the action is checked.

        """
        self.widget.setChecked(checked)

    def set_status_tip(self, status_tip):
        """ Sets the status tip text for the action.

        """
        self.widget.setStatusTip(status_tip)
    
    def set_tool_tip(self, tool_tip):
        """ Sets the tool tip text for the action.

        """
        self.widget.setToolTip(tool_tip)
    
    def set_description(self, description):
        """ Sets the description text for the action.

        """
        self.widget.setWhatsThis(description)

    def set_separator(self, separator):
        """ Sets whether or not the QAction is a separator.

        """
        self.widget.setSeparator(separator)

    def enable_updates(self):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QAction.

        """
        pass
    
    def disable_updates(self):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QAction.

        """
        pass

