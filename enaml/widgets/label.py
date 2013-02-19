#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from atom.api import Unicode, Enum, observe, set_default

from enaml.core.declarative import d_properties

from .control import Control


@d_properties('text', 'align', 'vertical_align')
class Label(Control):
    """ A simple control for displaying read-only text.

    """
    #: The unicode text for the label.
    text = Unicode()

    #: The horizontal alignment of the text in the widget area.
    align = Enum('left', 'right', 'center', 'justify')

    #: The vertical alignment of the text in the widget area.
    vertical_align = Enum('center', 'top', 'bottom')

    #: Labels hug their width weakly by default.
    hug_width = set_default('weak')

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the dict of creation attributes for the control.

        """
        snap = super(Label, self).snapshot()
        snap['text'] = self.text
        snap['align'] = self.align
        snap['vertical_align'] = self.vertical_align
        return snap

    @observe(r'^(text|align|vertical_align)$', regex=True)
    def send_member_change(self, change):
        """ An observe which sends the state change to the client.

        """
        # The superclass implementation is sufficient.
        super(Label, self).send_member_change(change)

