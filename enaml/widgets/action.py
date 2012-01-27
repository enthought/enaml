#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Bool, Unicode

from .component import Component, AbstractTkComponent

from ..core.trait_types import EnamlEvent


class AbstractTkAction(AbstractTkComponent):
    """ The abstract toolkit interface for an Action.

    """
    @abstractmethod
    def shell_text_changed(self, text):
        """ The change handler for the 'text' attribute on the shell
        object.

        """
        raise NotImplementedError
        
    @abstractmethod
    def shell_status_tip_changed(self, status_tip):
        """ The change handler for the 'status_tip' attribute on the 
        shell object.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_tool_tip_changed(self, tool_tip):
        """ The change handler for the 'tool_tip' attribute on the 
        shell object.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_description_changed(self, description):
        """ The change handler for the 'description' attribute on the 
        shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_checkable_changed(self, checkable):
        """ The change handler for the 'checkable' attribute on the 
        shell object.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_checked_changed(self, checked):
        """ The change handler for the 'checked' attribute on the
        shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_separator_changed(self, separator):
        """ The change handler for the 'separator' attribute on the
        shell object.

        """
        raise NotImplementedError


class Action(Component):
    """ A declarative Enaml component which represents an action 
    associated with a menu or toolbar.

    """
    #: The text label associate with the action.
    text = Unicode

    #: The text that is displayed in the status bar when the user
    #: hovers over the action.
    status_tip = Unicode

    #: The tool tip text to use for this action. Typically displayed
    #: as small label when the user hovers over the action.
    tool_tip = Unicode

    #: The description text to use for this action, such as context
    #: sensitive help. This is typically more descriptive that the
    #: tool tip text.
    description = Unicode

    #: An event fired when the action is triggered by user interaction.
    triggered = EnamlEvent

    #: An event fired when the user hovers over the action.
    hovered = EnamlEvent

    #: An event fired when a checkable action changes its checked state.
    toggled = EnamlEvent

    #: Whether or not the action can be checked.
    checkable = Bool(False)

    #: Whether or not the action is checked. This value only has meaning
    #: if 'checkable' is set to True.
    checked = Bool(False)

    #: Whether or not the action should be considered a separator.
    separator = Bool(False)

    # XXX need to handle icons and keyboard shortcuts

