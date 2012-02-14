#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import (
    Property, Int, Instance, List, cached_property, on_trait_change,
)

from .constraints_widget import (
    ConstraintsWidget, AbstractTkConstraintsWidget,
)
from .layout_task_handler import LayoutTaskHandler
from .tab import Tab

from ..enums import TabPosition


class AbstractTkTabGroup(AbstractTkConstraintsWidget):
    """ The abstract toolkit TabGroup interface.

    """
    @abstractmethod
    def shell_tabs_changed(self, tabs):
        """ The change handler for the 'tabs' attribute of the shell 
        object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_tab_position_changed(self, tab_position):
        """ The change handler for the 'tab_position' attribute on the 
        shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_selected_index_changed(self, index):
        """ The change handler for the 'selected_index' attribute on
        the shell object.

        """
        raise NotImplementedError


class TabGroup(LayoutTaskHandler, ConstraintsWidget):
    """ A LayoutComponent that arranges its children as a group of tabs.

    The TabGroup provides a very simple way of laying out a number of 
    children as tabs, suitable for configuration dialogs and the like. 
    It is not suitable for rich tab interfaces where the group of tabs
    is the central focus of the application. For that, use a Notebook.

    """
    #: A read-only cached property that returns the tab children
    #: of this tab group.
    tabs = Property(List(Instance(Tab)), depends_on='children')

    #: A readonly property which returns the selected index. If there 
    #: are no tabs in the group, this will return -1.
    selected_index = Property(Int, depends_on='_selected_index')

    #: A readonly property which returns the selected tab. If there are 
    #: no tabs in the group, this will return None.
    selected_tab = Property(Instance(Tab), depends_on='_selected_index')

    #: A TabPosition enum value that indicate where the tabs should
    #: be drawn on the control. One of 'top', 'bottom', 'left', 'right'.
    #: The default value is 'top'.
    tab_position = TabPosition('top')

    #: How strongly a component hugs it's contents' width. A TabGroup
    #: ignores its width hug by default, so it expands freely in width.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. A TabGroup
    #: ignores its height hug by default, so it expands freely in height.
    hug_height = 'ignore'

    #: The private storage for the selected tab index. This attribute
    #: should be used by the toolkit implementations to communicate the 
    #: current selection. A -1 indicates no selection.
    _selected_index = Int(-1)

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkTabGroup)
    
    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_tabs(self):
        """ The property getter for the 'tabs' attribute.

        """
        flt = lambda child: isinstance(child, Tab)
        return filter(flt, self.children)
    
    def _get_selected_tab(self):
        """ The property getter for the 'selected_tab' attribute.

        """
        idx = self._selected_index
        tabs = self.tabs
        n = len(tabs)
        if 0 <= idx < n:
            res = tabs[idx]
        elif idx == -1 and n > 0:
            res = tabs[0]
        else:
            res = None
        return res
    
    def _get_selected_index(self):
        """ The property getter for the 'selected_index' attribute.

        """
        idx = self._selected_index
        if idx == -1 and len(self.tabs) > 0:
            idx = 0
        return idx

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    @on_trait_change('tabs, tab_position')
    def _on_tab_group_deps_changed(self):
        """ A change handler for triggering a relayout when the tabs or
        the position of the tabs change, provided that the component
        is initialized.

        """
        if self.initialized:
            self.request_relayout()

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def do_relayout(self):
        """ A reimplemented LayoutTaskHandler handler method which will
        perform necessary update activity when a relayout is requested.

        """
        self.size_hint_updated()

    #--------------------------------------------------------------------------
    # Auxiliary Methods 
    #--------------------------------------------------------------------------
    def set_selected_tab(self, tab):
        """ Set the selected tab of the group to the given tab.

        """
        try:
            idx = self.tabs.index(tab)
        except ValueError:
            msg = ('Cannot set selected tab. Tab %s does not exist in '
                   'the TabGroup')
            raise ValueError(msg % tab)
        self._selected_index = idx
    
    def set_selected_index(self, idx):
        """ Set the selected index of the group to the given index.

        """
        if idx < 0 or idx >= len(self.tabs):
            msg = "Tab index %s out of range for TabGroup"
            raise IndexError(msg % idx)
        self._selected_index = idx

