#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from atom.api import ForwardInstance, observe

from enaml.core.declarative import d

from .constraints_widget import PolicyEnum
from .control import Control


def Component():
    """ The Enable Component resolver.

    This removes the import dependency on Enable.

    """
    from enaml.component import Component
    return Component


class EnableCanvas(Control):
    """ A control which can be used to embded an Enable component.

    """
    #: The enable.component.Component instance to draw.
    component = d(ForwardInstance(Component))

    #: An EnableCanvas expands freely in width and height by default.
    hug_width = d(PolicyEnum('ignore'))
    hug_height = d(PolicyEnum('ignore'))

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

