#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Property, cached_property

from .action import Action
from .widget_component import WidgetComponent


class Menu(WidgetComponent):
    """ A widget used as a menu in a MenuBar.

    """
    #: The title to use for the menu.
    title = Unicode
    
    #: The menu items in the menu. These will be instances of either 
    #: Action or Menu
    menu_items = Property(depends_on='children[]')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the Menu.

        """
        snap = super(Menu, self).snapshot()
        snap['menu_item_ids'] = self._snap_menu_item_ids()
        snap['title'] = self.title
        return snap

    def bind(self):
        """ Bind the change handlers for the menu.

        """
        super(Menu, self).bind()
        self.publish_attributes('title')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_menu_items(self):
        """ The getter for the 'menu_items' property.

        Returns
        -------
        result : tuple
            The tuple of Actions or Menus defined as children of this 
            Menu.

        """
        isinst = isinstance
        allowed = (Action, Menu)
        items = (child for child in self.children if isinst(child, allowed))
        return tuple(items)

    def _snap_menu_item_ids(self):
        """ Returns the list of widget ids for the menu items.

        """
        return [item.widget_id for item in self.menu_items]

