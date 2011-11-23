#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import List, Instance, Property, on_trait_change

from .stacked import Stacked, AbstractTkStacked
from .tab import Tab

from ..enums import TabPosition


_SIZE_HINT_DEPS = ('children:size_hint_updated, children:hug_width, '
                   'children:hug_height, children:resist_clip_width, '
                   'children:resist_clip_height')


class AbstractTkTabbed(AbstractTkStacked):
    """ The abstract toolkit Tabbed interface.

    """
    @abstractmethod
    def shell_tab_position_changed(self, tab_position):
        """ The change handler for the 'tab_position' attribute on the 
        shell object.

        """
        raise NotImplementedError


class Tabbed(Stacked):
    """ A Stacked subclass that arranges its children in a tabbed 
    layout. 

    The Tabbed container provides a very simple way of laying out a 
    fixed number of children as tabs, suitable for configuration dialogs 
    and the like. It is not suitable for dynamci use cases since it does 
    not support features such as: add new tabs, closing tabs, or docking
    or otherwise rearranging tabs. Further, on platforms that support it,
    the Tabbed container is rendered in non-document style (i.e. the
    style used for static dialogs).

    For document-style tabs that support all of the dynamic goodies,
    use the TabbedList component.

    """
    #: A TabPosition enum value that indicate where the tabs should
    #: be drawn on the control. One of 'top', 'bottom', 'left', 'right'.
    #: The default value is 'top'.
    tab_position = TabPosition('top')

    #: A get/set property for the currently selected tab object in 
    #: the container. Synchronized with :attr:`index`.
    selected = Property(depends_on='index')

    #: Overridden parent class trait. Children of a Tabbed container
    #: must be Tab instances.
    children = List(Instance(Tab))

    #--------------------------------------------------------------------------
    # Property Handlers 
    #--------------------------------------------------------------------------
    def _get_selected(self):
        """ The property getter for the 'selected' attribute. Returns
        the selected child or None if there are no children.

        """
        children = self.children
        if len(children) == 0:
            res = None
        else:
            res = children[self.index]
        return res
    
    def _set_selected(self, selected):
        """ The property setter for the 'selected' attribute. Sets
        the index to represent the given tab or raises a Value error
        if the given tab is not a child of this container.

        """
        try:
            idx = self.children.index(selected)
        except ValueError:
            msg = '%s is not a child of the Tabbed container' % selected
            raise ValueError(msg)
        self.index = idx

    @on_trait_change(_SIZE_HINT_DEPS)
    def handle_size_hint_changed(self, child, name, old, new):
        """ Pass up the size hint changed notification to the parent
        so that a window resize can take place if necessary.

        """
        self.size_hint_updated = True

