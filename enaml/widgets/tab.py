#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Property, cached_property

from .container import Container
from .widget_component import WidgetComponent


class Tab(WidgetComponent):
    """ A widget which can be used as a tab in a TabControl.

    A Tab is a widget which can be used as a child of a TabControl.
    It can have at most a single child widget which is an instance 
    of Container.

    """
    #: The title to use for the tab in the control.
    title = Unicode

    #: The icon to user for the tab in the control.
    # icon = 

    #: The tool tip to use when the user hovers over the tab.
    tool_tip = Unicode

    #: A read only property which returns the tab's tab widget.
    tab_widget = Property(depends_on='children[]')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the snapshot for the control.

        """
        snap = super(Tab, self).snapshot()
        snap['tab_widget_id'] = self._snap_tab_widget_id()
        snap['title'] = self.title
        snap['tool_tip'] = self.tool_tip
        return snap

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(Tab, self).bind()
        self.publish_attributes('title', 'tool_tip')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_tab_widget(self):
        """ The getter for the 'tab_widget' property.

        Returns
        -------
        result : Container or None
            The tab widget for the Tab, or None if not provided.

        """
        for child in self.children:
            if isinstance(child, Container):
                return child

    def _snap_tab_widget_id(self):
        """ Returns the widget id for the tab widget or None.

        """
        tab_widget = self.tab_widget
        if tab_widget is not None:
            return tab_widget.widget_id

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open(self):
        """ Open the tab in the control.

        Calling this method will also set the tab visibility to True.

        """
        self.set_guarded(visible=True)
        self.send_action('open', {})

    def close(self):
        """ Close the tab in the control.

        Calling this method will set the tab visibility to False.

        """ 
        self.set_guarded(visible=False)
        self.send_action('close', {})

