#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Bool, Instance, Str

from .container import Container, AbstractTkContainer

from ..enums import HorizontalAlign
from ..layout.box_model_mixin import MarginBoxModelMixin


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


class GroupBox(MarginBoxModelMixin, Container):
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

