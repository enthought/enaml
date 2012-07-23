#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum
from .tab_bar import TabBar


class Notebook(TabBar):
    """ A component which displays its children as tabbed pages.

    """
    #: The position of tabs in the notebook.
    tab_position = Enum('top', 'bottom', 'left', 'right')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Return the dict of creation attributes for the control.

        """
        super_attrs = super(Notebook, self).creation_attributes()
        attrs = {
            'tab_position': self.tab_position
        }
        super_attrs.update(attrs)
        return super_attrs

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(Notebook, self).bind()
        attrs = ('tab_position')
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_message_tab_closed(self, payload):
        """ Handle the 'tab-closed' action from the client widget.

        """
        target_id = payload['target_id']
        for child in self.children:
            if child.target_id == target_id:
                self.tab_closed(child)
                child.closed()
                return

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open_tab(self, page):
        """ Open the tab for the given page, if it isn't already open.

        Parameters
        ----------
        page : Page
            The page instance to open. It must be a child of this
            Notebook.

        """
        assert page in self.children, "Page is not a child of the Notebook"
        payload = {'action': 'open-tab', 'target_id': page.target_id}
        self.send_message(payload)

    def close_tab(self, page):
        """ Close the tab for the given page, if it isn't already closed.

        Parameters
        ----------
        page : Page
            The page instance to close. It must be a child of this
            Notebook.

        """
        assert page in self.children, "Page is not a child of the Notebook"
        payload = {'action': 'close-tab', 'target_id': page.target_id}
        self.send_message(payload)

