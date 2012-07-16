#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Bool

from enaml.core.trait_types import EnamlEvent

from .container import Container


class Page(Container):
    """ A component which is used as a page in a Notebook control.

    """
    #: The title to use for the page in the notebook.
    title = Unicode

    #: The icon to user for the page in the notebook.
    # icon = 

    #: The tool tip to use for a page when the user hovers a tab.
    tool_tip = Unicode

    #: Whether or not the tab for the page should be enabled. Note
    #: that this is different from 'enabled' which applies to the 
    #: page itself as opposed to the tab for the page.
    tab_enabled = Bool(True)

    #: Whether or not this particular tab is closable through user
    #: interaction. Note that the 'tabs_closable' attribute on the
    #: parent Notebook must be set to True for this to have any 
    #: affect. Also note that whether or not to draw a close button
    #: for a non-closable Page in a Notebook where tabs are closable
    #: is left up to the client implementation.
    closable = Bool(True)

    #: An event fired when the user closes the page by clicking on 
    #: the tab's close button.
    closed = EnamlEvent

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Return the dict of creation attributes for the control.

        """
        super_attrs = super(Page, self).creation_attributes()
        super_attrs['title'] = self.title
        super_attrs['tool_tip'] = self.tool_tip
        super_attrs['tab_enabled'] = self.tab_enabled
        super_attrs['closable'] = self.closable
        return super_attrs

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(Page, self).bind()
        self.publish_attributes('title', 'tool_tip', 'tab_enabled', 'closable')

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_message_closed(self, payload):
        """ Handle the 'closed' action from the client widget.

        """
        self.closed()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open(self):
        """ Open the tab for this page, if it isn't already open.

        """
        payload = {'action': 'open'} 
        self.send_message(payload)

    def close(self):
        """ Close the tab for this page, if it isn't already closed.

        """
        payload = {'action': 'close'}
        self.send_message(payload)

