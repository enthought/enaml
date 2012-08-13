#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from .menu import Menu
from .widget_component import WidgetComponent


class MenuBar(WidgetComponent):
    """ A widget used as a menu bar in a MainWindow.

    """
    #: A read only property which returns the menu bar's menus.
    menus = Property(depends_on='children')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the DockPane.

        """
        snap = super(MenuBar, self).snapshot()
        snap['menu_ids'] = self._snap_menu_ids()
        return snap

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_menus(self):
        """ The getter for the 'menus' property.

        Returns
        -------
        result : tuple
            The tuple of Menus defined as children of this MenuBar.

        """
        isinst = isinstance
        menus = (child for child in self.children if isinst(child, Menu))
        return tuple(menus)

    def _snap_menu_ids(self):
        """ Returns the list of widget ids for the menus.

        """
        return [menu.widget_id for menu in self.menus]

