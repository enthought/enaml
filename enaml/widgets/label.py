#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Enum

from .control import Control


class Label(Control):
    """ A simple control for displaying read-only text.

    """
    #: The text for the label.
    text = Unicode

    #: The horizontal alignment of the text in the widget area.
    align = Enum('left', 'right', 'center', 'justify')

    #: The vertical alignment of the text in the widget area.
    vertical_align = Enum('center', 'top', 'bottom')

    #: How strongly a component hugs it's content. Labels hug their
    #: contents' width weakly by default.
    hug_width = 'weak'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the dict of creation attributes for the control.

        """
        snap = super(Label, self).snapshot()
        snap['text'] = self.text
        snap['align'] = self.align
        snap['vertical_align'] = self.vertical_align
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Label, self).bind()
        self.publish_attributes('text', 'align', 'vertical_align')

