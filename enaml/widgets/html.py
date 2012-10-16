#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str

from .control import Control


class Html(Control):
    """ An extremely simple widget for displaying HTML.

    """
    #: The Html source code to be rendered.
    source = Str

    #: How strongly a component hugs it's contents' width. Html widgets
    #: ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. Html widgets
    #: ignore the height hug by default, so they expand freely in height.
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the dictionary of creation attributes for the control.

        """
        snap = super(Html, self).snapshot()
        snap['source'] = self.source
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Html, self).bind()
        self.publish_attributes('source')

