#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Property, cached_property

from .constraints_widget import ConstraintsWidget
from .tab import Tab


class TabControl(ConstraintsWidget):
    """ A component which displays its children as tabs.

    A TabControl is similar to a Notebook, but more limited in features.
    It is typically used in a dialog or windows for setting preferences
    and rendered in a fashion appropriate for that task. The tabs in a 
    tab control are not closable, dockable, or movable by the user.

    """
    #: The position of the tabs in the control.
    tab_position = Enum('top', 'bottom', 'left', 'right')

    #: A read only property which returns the tab control's tabs.
    tabs = Property(depends_on='children[]')

    #: How strongly a component hugs it's contents' width. A TabControl
    #: ignores its width hug by default, so it expands freely in width.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. A TabControl
    #: ignores its height hug by default, so it expands freely in height.
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the snapshot for the control.

        """
        snap = super(TabControl, self).snapshot()
        snap['tab_ids'] = self._snap_tab_ids()
        snap['tab_position'] = self.tab_position
        return snap

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(TabControl, self).bind()
        self.publish_attributes('tab_position')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_tabs(self):
        """ The getter for the 'tabs' property.

        Returns
        -------
        result : tuple
            The tuple of Tab instances defined as children of this
            TabControl.

        """
        isinst = isinstance
        tabs = (child for child in self.children if isinst(child, Tab))
        return tuple(tabs)

    def _snap_tab_ids(self):
        """ Returns the widget ids of the tab control's tabs.

        """
        return [tab.widget_id for tab in self.tabs]

