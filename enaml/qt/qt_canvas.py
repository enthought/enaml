#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from .qt_constraints_widget import QtConstraintsWidget


class QtCanvas(QtConstraintsWidget):
    """ A Qt4 wrapper around a canvas that exports a Qt widget.

    """
    def create_widget(self, parent, tree):
        """ Creates the underlying Qt widget using Enable's
            EnableWindow wrapper

        """
        component = tree['component']

        # Need to create the widget here, since I need access to the component
        from enable.api import Window as EnableWindow
        self._window = EnableWindow(parent, component=component)

        return self._window.control
