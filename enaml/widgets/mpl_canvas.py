#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#
# Special thanks to Steven Silvester for contributing this module!
#------------------------------------------------------------------------------
# NOTE: There shall be no imports from matplotlib in this module. Doing so
# will create an import dependency on matplotlib for the rest of Enaml!
from traits.api import Instance, Bool

from .control import Control


class MPLCanvas(Control):
    """ A control which can be used to embded a matplotlib figure.

    """
    #: The matplotlib figure to display in the widget.
    figure = Instance('matplotlib.figure.Figure')

    #: Whether or not the matplotlib figure toolbar is visible.
    toolbar_visible = Bool(False)

    #: Matplotlib figures expand freely in height and width by default.
    hug_width = 'ignore'
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dict for the MPLCanvas.

        """
        snap = super(MPLCanvas, self).snapshot()
        snap['figure'] = self.figure
        snap['toolbar_visible'] = self.toolbar_visible
        return snap

    def bind(self):
        """ Bind the change handlers for the MPLCanvas.

        """
        super(MPLCanvas, self).bind()
        self.publish_attributes('figure', 'toolbar_visible')

