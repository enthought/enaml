#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
# NOTE: There shall be no imports from enable in this module. Doing so
# will create an import dependency on enable for the rest of Enaml!
from traits.api import Instance

from .control import Control


class EnableCanvas(Control):
    """ A control which can be used to embded an Enable component.

    """
    #: The enable.component.Component instance to draw.
    component = Instance('enable.component.Component')

    #: An EnableCanvas expands freely in width and height by default.
    hug_width = 'ignore'
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dict for the canvas.

        """
        snap = super(EnableCanvas, self).snapshot()
        snap['component'] = self.component
        return snap

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(EnableCanvas, self).bind()
        self.publish_attributes('component')

