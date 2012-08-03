#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from enable.api import Window as EnableWindow

from .qt_constraints_widget import QtConstraintsWidget


class QtCanvas(QtConstraintsWidget):
    """ A Qt4 wrapper around an image canvas.

    """
    def create_widget(self, parent, tree):
        """ Initialize the widget's attributes.

        """
        # Need to create the widget here, since I need access to the component
        component = tree['component']
        self._window = EnableWindow(parent, component=component)
        return self._window.control
