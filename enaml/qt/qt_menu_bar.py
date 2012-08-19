#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QMenuBar
from .qt_widget_component import QtWidgetComponent


class QtMenuBar(QtWidgetComponent):
    """ A Qt implementation of an Enaml MenuBar.

    """
    #: Storage for the menu ids.
    _menu_ids = []

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying menu bar widget.

        """
        return QMenuBar(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtMenuBar, self).create(tree)
        self.set_menu_ids(tree['menu_ids'])

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtMenuBar, self).init_layout()
        widget = self.widget()
        find_child = self.find_child
        for menu_id in self._menu_ids:
            child = find_child(menu_id)
            if child is not None:
                widget.addMenu(child.widget())
        
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_menu_ids(self, menu_ids):
        """ Set the menu ids for the underlying control.

        """
        self._menu_ids = menu_ids

