#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str, Enum

from .container import Container

from ..layout.geometry import Box


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
    title_align = Enum('left', 'right', 'center')

    def creation_attributes(self):
        """ Populates the initial attributes dict for the component.

        """
        super_attrs = super(GroupBox, self).creation_attributes()
        super_attrs['title'] = self.title
        super_attrs['flat'] = self.flat
        super_attrs['title_align'] = self.title_align
        return super_attrs

    def _padding_constraints(self):
        """ Overriden padding constraints method to add the contents 
        margins of the underlying group box to the specified user 
        padding.

        """
        cns = []
        #margin_box = self.abstract_obj.get_contents_margins()
        margin_box = Box(0, 0, 0, 0)
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

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(GroupBox, self).bind()
        self.publish_attributes('title', 'title_align', 'flat')

