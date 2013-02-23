#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from traits.api import Any

from enaml.widgets.control import Control

class EmbedWidget(Control):
    """ An Enaml widget that embeds an underlying toolkit widget

    """
    #: The QWidget subclass we are embedding
    widget = Any()

    #: A generic widget expands freely
    hug_width = 'ignore'

    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Create the snapshot for the widget.

        """
        snap = super(EmbedWidget, self).snapshot()
        snap['widget'] = self.widget
        return snap

    def bind(self):
        """ Bind the change handlers for the widget.

        """
        super(EmbedWidget, self).bind()
        self.publish_attributes('widget')

