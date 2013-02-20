#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from atom.api import ForwardInstance, observe, set_default

from enaml.core.declarative import d_

from .control import Control


def Component():
    """ The Enable Component resolver.

    This removes the import dependency on Enable.

    """
    from enable.component import Component
    return Component


class EnableCanvas(Control):
    """ A control which can be used to embded an Enable component.

    """
    #: The enable.component.Component instance to draw.
    component = d_(ForwardInstance(Component))

    #: An EnableCanvas expands freely in width and height by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #--------------------------------------------------------------------------
    # Messaging API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dict for the canvas.

        """
        snap = super(EnableCanvas, self).snapshot()
        snap['component'] = self.component
        return snap

    @observe('component')
    def send_member_change(self, change):
        """ An observer which sends the state change to the client.

        """
        # The superclass implementation is sufficient.
        super(EnableCanvas, self).send_member_change(change)

