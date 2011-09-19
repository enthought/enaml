#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui

from traits.api import implements

from .qt_stacked_group import QtStackedGroup

from ..tab_group import ITabGroupImpl


class QtTabGroup(QtStackedGroup):
    """ A Qt implementation of TabGroup.

    See Also
    --------
    TabGroup

    """
    implements(ITabGroupImpl)

    #---------------------------------------------------------------------------
    # IStackGroupImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying QTabWidget.

        """
        self.widget = QtGui.QTabWidget(parent=self.parent_widget())
        self.bind()

    def initialize_widget(self):
        """ Initialize the QtTabGroup.

        """
        super(QtTabGroup, self).initialize_widget()
        self.set_movable_flag(self.parent.movable)

    def layout_child_widgets(self):
        """ Layout the contained pages.

        """
        self_add_tab = self.widget.addTab
        self_parent_children = self.parent.children
        wrapped_children = self.wrap_child_containers()
        
        for i, child_wrapper in enumerate(wrapped_children):
            self_add_tab(child_wrapper, self_parent_children[i].name)
            
        self.set_page(self.parent.current_index)

    def parent_movable_changed(self, movable):
        """ Update the movable style in the tab

        Arguments
        ---------
        movable : boolean
            When true the tabs are allowd to be moved around by dragging

        """
        self.set_movable_flag(movable)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def bind(self):
        """ Bind to the flatnotebook widget events.

        """
        tab_bar = self.widget.tabBar()
        tab_bar.tabMoved.connect(self.on_tab_moved)

    def on_tab_moved(self, to_idx, from_idx):
        """ Event handler for the 'tabMoved' signal on the QTabWidget's QTabBar.
        
        """
        self.parent.current_index = to_idx
        self.parent.reordered = (from_idx, to_idx)

    def set_movable_flag(self, movable):
        """ Set the movable style in the widget

        Arguments
        ---------
        movable : boolean
            When true the pages can be moved around

        """
        self.widget.setMovable(movable)
