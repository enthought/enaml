#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Unicode, Enum

from .container import Container


class GroupBox(Container):
    """ The GroupBox container, which introduces a group of widgets with 
    a title and usually has a border.

    """
    #: The title displayed at the top of the box.
    title = Unicode

    #: The flat parameter determines if the GroupBox is displayed with 
    #: just the title and a header line (True) or with a full border 
    #: (False, the default).
    flat = Bool(False)

    #: The alignment of the title text.
    title_align = Enum('left', 'right', 'center')

    def snapshot(self):
        """ Populates the initial attributes dict for the component.

        """
        snap = super(GroupBox, self).snapshot()
        snap['title'] = self.title
        snap['flat'] = self.flat
        snap['title_align'] = self.title_align
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(GroupBox, self).bind()
        self.publish_attributes('title', 'title_align', 'flat')

