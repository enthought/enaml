#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, Property, Tuple, Enum, on_trait_change

from .widget_component import WidgetComponent, AbstractTkWidgetComponent

from ..layout.constrainable import Constrainable
from ..layout.geometry import Rect


PolicyEnum = Enum('ignore', 'weak', 'medium', 'strong', 'required')


#------------------------------------------------------------------------------
# Abstract Toolkit Constraints Widget Interface
#------------------------------------------------------------------------------
class AbstractTkConstraintsWidget(AbstractTkWidgetComponent):
    """ The abstract toolkit ConstraintsWidget interface.

    """
    pass


#------------------------------------------------------------------------------
# ConstraintsWidget
#------------------------------------------------------------------------------
class ConstraintsWidget(WidgetComponent, Constrainable):
    """ A WidgetComponent subclass which mixes in the Constrainable
    interface and adds some additional hints for being managed by 
    a Container.

    """
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
        Tuple(PolicyEnum, PolicyEnum), depends_on='hug_width, hug_height',
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
        depends_on='resist_clip_width, resist_clip_height',
    )

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkConstraintsWidget)

    #--------------------------------------------------------------------------
    # Property Getters and Setters
    #--------------------------------------------------------------------------
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
    # Change Handlers
    #--------------------------------------------------------------------------
    @on_trait_change('hug, resist_clip')
    def _on_constraints_widget_deps_changed(self):
        """ A handler which requests a relayout from the *parent* when
        the 'hug' or 'resist_clip' values change, provided that the 
        component is initialized. 

        Note that it is critical that the request is made to the parent
        since the component itself has not use for its size hint in 
        its own internal layout calculations.

        """
        if self.initialized:
            parent = self.parent
            if parent is not None:
                parent.request_relayout()
    
    #--------------------------------------------------------------------------
    # Constraint Handlers
    #--------------------------------------------------------------------------
    def size_hint_constraints(self):
        """ Returns the list of constraints relating to the size hint 
        of this layout component. If the size hint in a given dimension
        is negative, then no constraints will be generated for that
        dimension.

        """
        cns = []
        push = cns.append

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
                push(cn)
            if resist_clip_width != 'ignore':
                cn = (width >= width_hint) | resist_clip_width
                push(cn)
        
        if height_hint >= 0:
            if hug_height != 'ignore':
                cn = (height == height_hint) | hug_height
                push(cn)
            if resist_clip_height != 'ignore':
                cn = (height >= height_hint) | resist_clip_height
                push(cn)

        return cns
    
    #--------------------------------------------------------------------------
    # Constrainable Interface
    #--------------------------------------------------------------------------
    def update_layout_geometry(self, dx, dy):
        """ An implementation of the required abstract method of the 
        Constrainable mixin. This computes the new layout geometry
        rect and updates the underlying widget.

        """
        x = int(round(self.left.value))
        y = int(round(self.top.value))
        width = int(round(self.width.value))
        height = int(round(self.height.value))
        rect = Rect(x - dx, y - dy, width, height)
        self.set_layout_geometry(rect)
        return (x, y)

