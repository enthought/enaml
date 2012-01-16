#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (
    List, Instance, Property, Tuple, Event, Enum, cached_property,
)

from .component import Component, AbstractTkComponent
from .resizable import Resizable, AbstractTkResizable
from .stylable import Stylable, AbstractTkStylable
from .layout.box_model import BoxModel

from ..guard import guard


PolicyEnum = Enum('ignore', 'weak', 'medium', 'strong', 'required')


#------------------------------------------------------------------------------
# Abstract Toolkit Layout Component Interface
#------------------------------------------------------------------------------
class AbstractTkLayoutComponent(AbstractTkComponent, 
                                AbstractTkResizable, 
                                AbstractTkStylable):
    """ The abstract toolkit LayoutComponent interface.

    A toolkit layout component is responsible for handling changes on 
    a shell LayoutComponent and proxying those changes to and from its 
    internal toolkit widget.

    """
    pass


#------------------------------------------------------------------------------
# Enaml Layout Component
#------------------------------------------------------------------------------
class LayoutComponent(Component, Resizable, Stylable):
    """ A Component subclass that adds a box model and support for 
    constraints specification. This class represents the most basic
    widget in Enaml that can partake in constraints-base layout.

    """
    #: The list of children that can participate in constraints based
    #: layout. This list is composed of components in the list of 
    #: children that are instances of LayoutComponent.
    layout_children = Property(
        List(Instance('LayoutComponent')), depends_on='children',
    )

    #: How strongly a component hugs it's contents' width. Valid strengths
    #: are 'weak', 'medium', 'strong', 'required' and 'ignore'. Default is 
    #: 'strong'. This trait should be overridden on a per-control basis to
    #: specify a logical default for the given control.
    hug_width = PolicyEnum('strong')

    #: How strongly a component hugs it's contents' height. Valid strengths
    #: are 'weak', 'medium', 'strong', 'required' and 'ignore'. Default is
    #: 'strong'. This trait should be overridden on a per-control basis to 
    #: specify a logical default for the given control.
    hug_height = PolicyEnum('strong')

    #: The combination of (hug_width, hug_height).
    hug = Property(
        Tuple(PolicyEnum, PolicyEnum), depends_on=['hug_width', 'hug_height'],
    )

    #: How strongly a component resists clipping its contents. Valid 
    #: strengths are 'weak', 'medium', 'strong', 'required' and 'ignore'. 
    #: The default is 'strong' for width.
    resist_clip_width = PolicyEnum('strong')

    #: How strongly a component resists clipping its contents. Valid 
    #: strengths are 'weak', 'medium', 'strong', 'required' and 'ignore'. 
    #: The default is 'strong' for height.
    resist_clip_height = PolicyEnum('strong')

    #: The combination of (resist_clip_width, resist_clip_height).
    resist_clip = Property(
        Tuple(PolicyEnum, PolicyEnum),
        depends_on=['resist_clip_width', 'resist_clip_height'],
    )

    #: An event that should be emitted by the abstract obj when its size 
    #: hint has updated due to some change.
    size_hint_updated = Event

    #: A read-only symbolic object that represents the left boundary of 
    #: the component
    left = Property

    #: A read-only symbolic object that represents the top boundary of 
    #: the component
    top = Property

    #: A read-only symbolic object that represents the width of the 
    #: component
    width = Property

    #: A read-only symbolic object that represents the height of the 
    #: component
    height = Property

    #: A read-only symbolic object that represents the right boundary 
    #: of the component
    right = Property

    #: A read-only symbolic object that represents the bottom boundary 
    #: of the component
    bottom = Property

    #: A read-only symbolic object that represents the vertical center 
    #: of the component
    v_center = Property

    #: A read-only symbolic object that represents the horizontal 
    #: center of the component
    h_center = Property

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkLayoutComponent)

    #: A private attribute that holds the box model instance
    #: for this component. 
    _box_model = Instance(BoxModel)
    def __box_model_default(self):
        return BoxModel(self)

    #--------------------------------------------------------------------------
    # Property Getters and Setters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_layout_children(self):
        """ Cached property getter for the 'layout_children' property. 
        This getter returns the sublist of children that are instances 
        of LayoutComponent.

        """
        flt = lambda child: isinstance(child, LayoutComponent)
        return filter(flt, self.children)

    def _get_left(self):
        """ Property getter for the 'left' property.

        """
        return self._box_model.left
    
    def _get_top(self):
        """ Property getter for the 'top' property.

        """
        return self._box_model.top
    
    def _get_width(self):
        """ Property getter for the 'width' property.

        """
        return self._box_model.width
    
    def _get_height(self):
        """ Property getter for the 'height' property.

        """
        return self._box_model.height
    
    def _get_right(self):
        """ Property getter for the 'right' property.

        """
        return self._box_model.right
    
    def _get_bottom(self):
        """ Property getter for the 'bottom' property.

        """
        return self._box_model.bottom
    
    def _get_v_center(self):
        """ Property getter for the 'v_center' property.

        """
        return self._box_model.v_center
    
    def _get_h_center(self):
        """ Property getter for the 'h_center' property.

        """
        return self._box_model.h_center

    def _get_hug(self):
        """ Property getter for the 'hug' property.

        """
        return (self.hug_width, self.hug_height)

    def _set_hug(self, value):
        """ Property setter for the 'hug' property.

        """
        width, height = value
        self.trait_set(hug_width=width, hug_height=height)

    def _get_resist_clip(self):
        """ Property getter for the 'resist_clip' property.

        """
        return (self.resist_clip_width, self.resist_clip_height)

    def _set_resist_clip(self, value):
        """ Property setter for the 'resist_clip' property.

        """
        width, height = value
        self.trait_set(resist_clip_width=width, resist_clip_height=height)

    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def _setup_init_layout(self):
        """ A reimplemented parent class setup method that performs any
        layout initialization necessary for the component. The layout is
        initialized from the bottom up.

        """
        super(LayoutComponent, self)._setup_init_layout()
        self.initialize_layout()

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _layout_children_changed(self):
        """ Handles the layout children being changed on this component 
        by requesting a relayout so long as this component has been 
        fully initialized.

        """
        if self.initialized:
            self.request_relayout()
    
    #--------------------------------------------------------------------------
    # Auxiliary Methods
    #--------------------------------------------------------------------------
    def initialize_layout(self):
        """ A method that is called when the layout of this component
        should be initialized. By default, this is a no-op. Subclasses
        should reimplement this method as necessary to initialize any
        required layouts.

        """
        pass
        
    def set_visible(self, visible):
        """ Set the visibility of the component according to the given
        boolean. This is a reimplemented parent class method that makes
        sure the appropriate relayout requests are made since a component
        that is not visible does not participate in constraints-based
        layout.

        """
        # Make sure the 'visible' attribute is synced up as a result
        # of the method call. This may fire a notification, in which
        # case the change handler will call this method again. This
        # guard prevents that unneeded recursion.
        if guard.guarded(self, 'set_visible'):
            return
        else:
            with guard(self, 'set_visible'):
                self.visible = visible

        # If the component is initialized but then the change must 
        # occur in a deferred context, since changing the visibility
        # of a layout component will require a constraints update.
        if self.initialized:
            self.request_relayout_task(self.abstract_obj.set_visible, visible)
        else:
            self.abstract_obj.set_visible(visible)

    def set_solved_geometry(self, root):
        """ Makes the component take the solved geometry and other 
        constrained variables and set its internal values.

        This method can assume that all of its parents have had their 
        geometry set correctly.

        Parameters
        ----------
        root : Container
            The root container that actually performed the layout for 
            this component. Implementations will need this to know how 
            to transform the global solved (x, y) values to local values 
            relative to their immediate parent.

        Returns
        -------
        dx, dy : int
            The offsets needed to convert (x, y) variable values into 
            local positions. These are mostly used in overrides of this 
            method that handle additional variables.

        """
        x = self.left.value
        y = self.top.value
        width = self.width.value
        height = self.height.value
        x, y, width, height = (int(round(z)) for z in (x, y, width, height))
        # This is offset against the root Container. Each Component's 
        # geometry actually needs to be offset against its parent. Walk 
        # up the tree and subtract out the parent's offset.
        dx = 0
        dy = 0
        for ancestor in self.traverse_ancestors(root):
            anc_dx, anc_dy, _, _ = ancestor.geometry()
            dx += anc_dx
            dy += anc_dy
        self.set_geometry(x - dx, y - dy, width, height)
        return (dx, dy)

