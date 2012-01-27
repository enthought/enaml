#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List, Instance, Property, Tuple, Enum, cached_property

from .component import Component, AbstractTkComponent
from .sizable import Sizable, AbstractTkSizable
from .stylable import Stylable, AbstractTkStylable
from .layout.box_model import BoxModel

from ..core.trait_types import EnamlEvent
from ..guard import guard


PolicyEnum = Enum('ignore', 'weak', 'medium', 'strong', 'required')


#------------------------------------------------------------------------------
# Abstract Toolkit Layout Component Interface
#------------------------------------------------------------------------------
class AbstractTkLayoutComponent(AbstractTkComponent, 
                                AbstractTkSizable, 
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
class LayoutComponent(Component, Sizable, Stylable):
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
    size_hint_updated = EnamlEvent

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
    # Layout Related Methods
    #--------------------------------------------------------------------------
    def initialize_layout(self):
        """ A method that is called when the layout of this component
        should be initialized. By default, this is a no-op. Subclasses
        should reimplement this method as necessary to initialize any
        required layouts.

        """
        pass

    def hard_constraints(self):
        """ Returns a list of constraints that must always apply to the 
        component under all circumstances. The default is to constrain
        the size and origin >= (0, 0). This method can be overridden 
        by sublasses to change the behavior.

        """
        c = [self.left >= 0, self.top >= 0, self.width >= 0, self.height >= 0]
        return c

    def size_hint_constraints(self):
        """ Returns the list of constraints relating to the size hint 
        of this layout component. The constraints generated here are 
        responsible for implementing the behavior defined by the 'hug' 
        and 'resist_clip' attributes.

        """
        cns = []
        
        width_hint, height_hint = self.size_hint()
        width = self.width
        height = self.height
        hug_width = self.hug_width
        hug_height = self.hug_height
        resist_clip_width = self.resist_clip_width
        resist_clip_height = self.resist_clip_height

        if width_hint >= 0:
            if hug_width != 'ignore':
                cn = (width == width_hint) | hug_width
                cns.append(cn)
            if resist_clip_width != 'ignore':
                cn = (width >= width_hint) | resist_clip_width
                cns.append(cn)
        
        if height_hint >= 0:
            if hug_height != 'ignore':
                cn = (height == height_hint) | hug_height
                cns.append(cn)
            if resist_clip_height != 'ignore':
                cn = (height >= height_hint) | resist_clip_height
                cns.append(cn)

        return cns
    
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

    def set_solved_geometry(self, dx, dy):
        """ Makes the component take the solved geometry and other 
        constrained variables and set its internal values.

        This method can assume that all of its parents have had their 
        geometry set correctly.

        Parameters
        ----------
        dx : int
            The x-direction offset of the parent of this component from
            the root component on which the solved dimensions are based.
        
        dy : int
            The y-direction offset of the parent of this component from
            the root component on which the solved dimensions are based.
        
        Returns
        -------
        result : (x, y)
            The solved (x, y) position of this component relative to
            the root component on which the solved dimensions are bsaed.

        """
        x = int(round(self.left.value))
        y = int(round(self.top.value))
        width = int(round(self.width.value))
        height = int(round(self.height.value))
        self.set_layout_geometry(x - dx, y - dy, width, height)
        return (x, y)

