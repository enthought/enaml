#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Bool, Instance, Str

from .container import Container, AbstractTkContainer

from ..enums import HorizontalAlign
from ..layout.geometry import Box


class AbstractTkGroupBox(AbstractTkContainer):
    """ The abstract toolkit GroupBox interface.

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
        """ Return the Box object of margin values for the widget.

        """
        return Box(0, 0, 0, 0)


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

    def padding_constraints(self):
        """ Overriden padding constraints method to add the contents 
        margins of the underlying group box to the specified user 
        padding.

        """
        cns = []
        margin_box = self.abstract_obj.get_contents_margins()
        user_padding = self.padding
        padding = map(sum, zip(margin_box, user_padding))
        tags = ('top', 'right', 'bottom', 'left')
        strengths = self.padding_strength
        if isinstance(strengths, basestring):
            strengths = (strengths,) * 4
        for tag, strength, padding in zip(tags, strengths, padding):
            tag = 'padding_' + tag
            sym = getattr(self, tag)
            cns.append(sym >= 0)
            if strength != 'ignore':
                cns.append((sym == padding) | strength)
        return cns

