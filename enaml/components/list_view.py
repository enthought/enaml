#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, Bool, Enum, Int, Property

from .abstract_item_view import AbstractItemView, AbstractTkItemView


class AbstractTkListView(AbstractTkItemView):
    """ The abstract toolkit interface for a ListView.

    """
    @abstractmethod
    def shell_view_mode_changed(self, mode):
        """ The change handler for the 'view_mode' attribute on the
        shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_resize_mode_changed(self, mode):
        """ The change handler for the 'resize_mode' attribute on the
        shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_wrapping_changed(self, wrapping):
        """ The change handler for the 'wrapping' attribute on the 
        shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell__flow_changed(self, flow):
        """ The change handler for the '_flow' attribute on the 
        shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_item_spacing_changed(self, spacing):
        """ The change handler for the 'item_spacing' attribute on
        the shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_uniform_item_sizes_changed(self, uniform):
        """ The change handler for the 'uniform_item_sizes' attribute
        on the shell object.

        """
        raise NotImplementedError


class ListView(AbstractItemView):
    """ A view for list data.
    
    """
    #: The viewing mode of the list view.
    view_mode = Enum('list', 'icon')

    #: Whether the items are fixed in place or adjusted during a resize.
    resize_mode = Enum('adjust', 'fixed')

    #: Whether item layout should wrap when there is not more visible
    #: space in the layout direction.
    wrapping = Bool(False)

    #: The directional flow of items in the layout. The 'default' flow
    #: will choose a flow which is appropriate for the given view mode.
    flow = Enum('default', 'top_to_bottom', 'left_to_right')

    #: A private trait which holds the computed flow value.
    _flow = Property(depends_on=['flow', 'view_mode'])

    #: The spacing between items in the layout.
    item_spacing = Int(0)

    #: Whether or not the items in the model have a uniform item size.
    uniform_item_sizes = Bool(False)

    #: How strongly a component hugs it's contents' height. ListViews 
    #: ignore the height hug by default, so they expand freely in height.
    hug_height = 'ignore'

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkListView)

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    def _get__flow(self):
        """ The property getter for the '_flow' property.

        """
        flow = self.flow
        mode = self.view_mode
        if flow == 'default':
            if mode == 'list':
                flow = 'top_to_bottom'
            else:
                flow = 'left_to_right'
        return flow

