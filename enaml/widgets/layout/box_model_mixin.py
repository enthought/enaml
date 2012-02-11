#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasStrictTraits, Property, Instance

from .box_model import BoxModel, MarginBoxModel


def _get_from_box_model(self, name):
    """ Property getter for all attributes that come from the box model.

    """
    return getattr(self._box_model, name)


class BoxModelMixin(HasStrictTraits):
    """ A mixin class which adds the constraints box model to the given
    BaseComponent subclass.

    """
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

    #: A private attribute that holds the box model instance
    #: for this component. 
    _box_model = Instance(BoxModel)
    def __box_model_default(self):
        return BoxModel(self)
    

class MarginBoxModelMixin(BoxModelMixin):
    """ A mixin class which adds the constraints margin box model to 
    the given BaseComponent subclass.

    """
    #: A read-only symbolic object that represents the internal left 
    #: margin of the container.
    margin_left = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal right 
    #: margin of the container.
    margin_right = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal top 
    #: margin of the container.
    margin_top = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal bottom 
    #: margin of the container.
    margin_bottom = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal left 
    #: boundary of the content area of the container.
    contents_left = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal right 
    #: boundary of the content area of the container.
    contents_right = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal top 
    #: boundary of the content area of the container.
    contents_top = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal bottom 
    #: boundary of the content area of the container.
    contents_bottom = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal width of
    #: the content area of the container.
    contents_width = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal height of
    #: the content area of the container.
    contents_height = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal center 
    #: along the vertical direction the content area of the container.
    contents_v_center = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal center 
    #: along the horizontal direction of the content area of the container.
    contents_h_center = Property(fget=_get_from_box_model)

    #: A private attribute that holds the box model instance for this 
    #: component.
    _box_model = Instance(MarginBoxModel)
    def __box_model_default(self):
        return MarginBoxModel(self)

