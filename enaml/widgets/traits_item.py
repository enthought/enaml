#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Instance, Any

from .control import Control


class TraitsItem(Control):
    """ A control to display a traitsui item

    """
    #: The item being displayed
    model = Instance(HasTraits)

    # optional : the desired handler for the model
    handler = Instance('Handler')

    # optional: the desired view for the model
    view = Any

    #: How strongly a component hugs it's contents' width. TraitsItems ignore
    #: the width hug by default, so they expand freely in width.
    hug_width = 'ignore'
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the dict of creation attributes for the control.

        """
        snap = super(TraitsItem, self).snapshot()
        snap['model'] = self.model
        snap['handler'] = self.handler
        snap['view'] = self.view
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(TraitsItem, self).bind()
        self.publish_attributes('model', 'handler', 'view')

