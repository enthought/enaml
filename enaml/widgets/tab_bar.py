#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Bool, List

from enaml.core.trait_types import EnamlEvent

from .constraints_widget import ConstraintsWidget


class TabBar(ConstraintsWidget):
    #: The tabs of the tab bar
    tabs = List
    #: The style of the tabs to use in the tab bar. This may not
    #: be supported on all platforms. The 'document' style is used
    #: when displaying many pages in an editing context such as in
    #: an IDE. The 'preferences' style is used to display tabs in
    #: a style that is appropriate for a preferences dialog. Such
    #: as used in OSX.
    tab_style = Enum('document', 'preferences')

    #: Whether or not the tabs in the tab bar should be closable.
    tabs_closable = Bool(True)

    #: Whether or not the tabs in the tab bar should be movable.
    tabs_movable = Bool(True)

    #: An event fired when the user adds a tab
    tab_added = EnamlEvent

    #: An event fired when the user changes tab
    tab_changed = EnamlEvent

    #: An event fired when the user closes a tab by clicking on its
    #: close button. The payload will be the page object.
    tab_closed = EnamlEvent

    #: An event fired when a tab is moved
    tab_moved = EnamlEvent

    #: How strongly a component hugs it's contents' width. A TabGroup
    #: ignores its width hug by default, so it expands freely in width.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. A TabGroup
    #: ignores its height hug by default, so it expands freely in height.
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Return the dict of creation attributes for the control.

        """
        super_attrs = super(TabBar, self).creation_attributes()
        attrs = {
            'tabs': self.tabs,
            'tab_style': self.tab_style,
            'tabs_closable': self.tabs_closable,
            'tabs_movable': self.tabs_movable
        }
        super_attrs.update(attrs)
        return super_attrs

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(TabBar, self).bind()
        attrs = ('tabs', 'tab_style', 'tabs_closable', 'tabs_movable')
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_message_tab_changed(self, payload):
        """ Handle the 'tab-changed' action from the client widget.

        """
        index = payload['index']
        self.tab_changed(index)

    def on_message_tab_closed(self, payload):
        """ Handle the 'tab-closed' action from the client widget.

        """
        index = payload['index']
        self.tab_closed(index)

    def on_message_tab_added(self, payload):
        """ Handle the 'tab-added' action from the client widget.

        """
        self.tab_added()

    def on_message_tab_moved(self, payload):
        """ Handle the 'tab-moved' action from the client widget.

        """
        self.tab_moved((payload['old'], payload['new']))

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def add_tab(self, title):
        """ Add a tab to the tab bar

        """
        self.tabs.append(title)
        payload = {
            'action': 'add-tab',
            'title': title
        }
        self.send_message(payload)

    def remove_tab(self, index):
        """ Remove a tab from the tab bar

        """
        self.tabs.pop(index)
        payload = {
            'action': 'remove-tab',
            'index': index
        }
        self.send_message(payload)
