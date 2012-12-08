#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance

from .control import Control


class MPLCanvas(Control):
    """ A control to display a Matplotlib Canvas

    """
    #: The figure
    figure = Instance('matplotlib.figure.Figure')

    #: How strongly a component hugs it's contents'.
    # MPLCanvas' ignore the hug by default,
    # so they expand freely in width and height.
    hug_width = 'ignore'
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the dict of creation attributes for the control.

        """
        snap = super(MPLCanvas, self).snapshot()
        snap['figure'] = self.figure
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(MPLCanvas, self).bind()
        self.publish_attributes('figure')
