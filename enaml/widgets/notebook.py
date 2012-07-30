#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Bool

from enaml.core.trait_types import EnamlEvent

from .constraints_widget import ConstraintsWidget


class Notebook(ConstraintsWidget):
    """ A component which displays its children as tabbed pages.

    """
    #: The position of tabs in the notebook.
    tab_position = Enum('top', 'bottom', 'left', 'right')

    #: The style of the tabs to use in the notebook. This may not
    #: be supported on all platforms. The 'document' style is used
    #: when displaying many pages in an editing context such as in
    #: an IDE. The 'preferences' style is used to display tabs in
    #: a style that is appropriate for a preferences dialog. Such
    #: as used in OSX.
    tab_style = Enum('document', 'preferences')

    #: Whether or not the tabs in the notebook should be closable.
    tabs_closable = Bool(True)

    #: Whether or not the tabs in the notebook should be movable.
    tabs_movable = Bool(True)

    #: An event fired when the user closes a tab by clicking on its
    #: close button. The payload will be the page object.
    tab_closed = EnamlEvent

    #: How strongly a component hugs it's contents' width. A TabGroup
    #: ignores its width hug by default, so it expands freely in width.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. A TabGroup
    #: ignores its height hug by default, so it expands freely in height.
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the dict of creation attributes for the control.

        """
        snap = super(Notebook, self).snapshot()
        attrs = {
            'tab_position': self.tab_position,
            'tab_style': self.tab_style,
            'tabs_closable': self.tabs_closable,
            'tabs_movable': self.tabs_movable,
        }
        snap.update(attrs)
        return snap

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(Notebook, self).bind()
        attrs = ('tab_position', 'tab_style', 'tabs_closable', 'tabs_movable')
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

