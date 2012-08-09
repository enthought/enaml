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

    #: Whether or not this individual page is closable. Note that the
    #: 'tabs_closable' flag on the parent Notebook must be set to True
    #: for this to have any effect.
    closable = Bool(True)

    #: An event fired when the user closes the page by clicking on 
    #: the tab's close button. This event is fired by the parent 
    #: Notebook when the tab is closed. This event has no payload.
    closed = EnamlEvent

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the dict of creation attributes for the control.

        """
        snap = super(Page, self).snapshot()
        snap['title'] = self.title
        snap['tool_tip'] = self.tool_tip
        snap['tab_enabled'] = self.tab_enabled
        snap['closable'] = self.closable
        return snap

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(Page, self).bind()
        self.publish_attributes('title', 'tool_tip', 'tab_enabled', 'closable')

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open(self):
        """ A convenience method for calling 'open_tab' on the parent
        Notebook, passing this page as an argument.

        """
        parent = self.parent
        if parent is not None:
            parent.open_tab(self)

    def close(self):
        """ A convenience method for calling 'close_tab' on the parent
        Notebook, passing this page as an argument.

        """ 
        parent = self.parent
        if parent is not None:
            parent.close_tab(self)

