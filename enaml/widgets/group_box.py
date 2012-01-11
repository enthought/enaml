#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Bool, Instance, Property, Str

from .container import Container, AbstractTkContainer
from .layout.box_model import MarginBoxModel

from ..enums import HorizontalAlign


def _get_from_box_model(self, name):
    """ Property getter for all attributes that come from the 
    MarginBoxModel.

    """
    return getattr(self._box_model, name)


class AbstractTkGroupBox(AbstractTkContainer):
    """ The abstract GroupBox interface.

    """

    @abstractmethod
    def shell_title_changed(self, title):
        """ Update the title of the group box with the new value from the
        shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_flat_changed(self, flat):
        """ Update the flat flag of the group box with the new value from 
        the shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_title_align_changed(self, align):
        """ Update the title alignment to the new value from the shell 
        object.

        """
        raise NotImplementedError

    @abstractmethod
    def get_contents_margins(self):
        """ Return the (top, left, right, bottom) margin values for the 
        widget.

        """
        return (0, 0, 0, 0)


class GroupBox(Container):
    """ The GroupBox container, which introduces a group of widgets with 
    a title and usually has a border.

    """
    #: The title displayed at the top of the box.
    title = Str()

    #: The flat parameter determines if the GroupBox is displayed with 
    #: just the title and a header line (True) or with a full border 
    #: (False, the default).
    flat = Bool(False)

    #: The alignment of the title text.
    title_align = HorizontalAlign

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkGroupBox)

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

    def container_constraints(self):
        """ A set of constraints that should always be applied to this 
        type of container.

        This sets up the definitions of the margins between the outer 
        boundaries of the container and its content rectangle.

        """
        top, left, right, bottom = self.abstract_obj.get_contents_margins()
        # These are 'required' constraints because they define immutable 
        # things.
        constraints = [
            (self.margin_top == top) | 'required',
            (self.margin_left == left) | 'required',
            (self.margin_right == right) | 'required',
            (self.margin_bottom == bottom) | 'required',
        ]
        return constraints

