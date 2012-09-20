#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance
from enable.component import Component as EnableComponent

from ..widgets.constraints_widget import ConstraintsWidget

class Canvas(ConstraintsWidget):
    """ An extremely simple widget for displaying an enable canvas
    
    """
    #: The enable component
    component = Instance(EnableComponent)
    
    #: How strongly a component hugs it's contents' width. Enable components
    #: ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'
    
    #: How strongly a component hugs it's contents' height. Enable components
    #: ignore the height hug by default, so they expand freely in height.
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot for the control

        """
        snap = super(Canvas, self).snapshot()
        snap['component'] = self.component
        return snap

    def bind(self):
        """ Bind the change handlers for the control

        """
        super(Canvas, self).bind()
        self.publish_attributes('component')

