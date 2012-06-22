#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from uuid import uuid4

from traits.api import Property, Tuple, Enum, Instance, List

from .constraint_variable import ConstraintVariable 
from .widget_component import WidgetComponent


class BoxModel(object):

    def __init__(self, owner):
        owner = str(owner)
        for primitive in ('left', 'top', 'width', 'height'):
            var = ConstraintVariable(primitive, owner)
            setattr(self, primitive, var) 
        self.right = self.left + self.width
        self.bottom = self.top + self.height
        self.v_center = self.top + self.height / 2.0
        self.h_center = self.left + self.width / 2.0   


def _get_from_box_model(self, name):
    """ Property getter for all attributes that come from the box model.

    """
    return getattr(self._box_model, name)


PolicyEnum = Enum('ignore', 'weak', 'medium', 'strong', 'required')


class ConstraintsWidget(WidgetComponent):
    """ A WidgetComponent subclass which mixes in the Constrainable
    interface and adds some additional hints for being managed by 
    a Container.

    """
    #: The list of user-specified constraints or constraint-generating
    #: objects for this component.
    constraints = List
        
    #: A unique identifier for this object to help distinguish its
    #: constraints from those of other objects.
    constraints_id = Instance(str, factory=lambda: uuid4().hex)

    #: A read-only symbolic object that represents the left boundary of 
    #: the component
    left = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the top boundary of 
    #: the component
    top = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the width of the 
    #: component
    width = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the height of the 
    #: component
    height = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the right boundary 
    #: of the component
    right = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the bottom boundary 
    #: of the component
    bottom = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the vertical center 
    #: of the component
    v_center = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the horizontal 
    #: center of the component
    h_center = Property(fget=_get_from_box_model)

    #: How strongly a component hugs it's width hint. Valid strengths
    #: are 'weak', 'medium', 'strong', 'required' and 'ignore'. Default 
    #: is 'strong'. This trait should be overridden on a per-control 
    #: basis to specify a logical default for the given control.
    hug_width = PolicyEnum('strong')

    #: How strongly a component hugs it's height hint. Valid strengths
    #: are 'weak', 'medium', 'strong', 'required' and 'ignore'. Default 
    #: is 'strong'. This trait should be overridden on a per-control 
    #: basis to specify a logical default for the given control.
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

    #: The private storage the box model instance for this component.
    _box_model = Instance(BoxModel)
    def __box_model_default(self):
        return BoxModel(self.constraints_id)

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

