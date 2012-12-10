#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QMdiSubWindow, QLayout
from .qt_widget import QtWidget


class QtMdiWindow(QtWidget):
    """ A Qt implementation of an Enaml MdiWindow.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QMdiSubWindow widget.

        """
        # We don't parent the subwindow immediately. It will be added
        # explicitly by the parent QMdiArea during its layout pass.
        # If we set the parent here, Qt will spit out warnings when
        # it's set added to the area later on. We *could* parent it
        # here, and simply not add it explicitly to the mdi area, but
        # this way is more explicit and consistent with the rest of
        # the framework.
        widget = QMdiSubWindow()
        widget.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        return widget

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtMdiWindow, self).init_layout()
        self._set_window_widget(self.mdi_widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def mdi_widget(self):
        """ Find and return the mdi widget child for this widget.

        Returns
        -------
        result : QWidget or None
            The mdi widget defined for this widget, or None if one is
            not defined.

        """
        widget = None
        for child in self.children():
            if isinstance(child, QtWidget):
                widget = child.widget()
        return widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtMdiWindow.

        """
        if isinstance(child, QtWidget):
            self._set_window_widget(self.mdi_widget())

    def child_added(self, child):
        """ Handle the child added event for a QtMdiWindow.

        """
        if isinstance(child, QtWidget):
            self._set_window_widget(self.mdi_widget())

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _set_window_widget(self, mdi_widget):
        """ A private method which set the child widget on the window.

        Parameters
        ----------
        mdi_widget : QWidget
            The child widget to use in the mdi window.

        """
        # We need to first set the window widget to None, or Qt will
        # complain if a widget is already set on the window.
        widget = self.widget()
        widget.setWidget(None)
        if mdi_widget is None:
            return
        # We need to unparent the underlying widget before adding
        # it to the subwindow. Otherwise, children like QMainWindow
        # will persist as top-level non-mdi widgets.
        mdi_widget.setParent(None)
        widget.setWidget(mdi_widget)
        # On OSX, the resize gripper will be obscured unless we
        # lower the widget in the window's stacking order.
        mdi_widget.lower()

