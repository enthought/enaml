#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QMdiSubWindow, QLayout
from .qt_widget_component import QtWidgetComponent


class QtMdiWindow(QtWidgetComponent):
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
        for child in self.children():
            if isinstance(child, QtWidgetComponent):
                self._set_window_widget(child.widget())
                break

    #--------------------------------------------------------------------------
    # Child Events 
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtMdiWindow.

        """
        for child in self.children():
            if isinstance(child, QtWidgetComponent):
                self._set_window_widget(child.widget())
                break

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _set_window_widget(self, widget):
        """ A private method which set the child widget on the window.

        Parameters
        ----------
        widget : QWidget
            The child widget to use in the window.

        """
        # We need to unparent the underlying widget before adding 
        # it to the subwindow. Otherwise, children like QMainWindow
        # will persist as top-level non-mdi widgets.
        widget.setParent(None)
        # We need to first set the window widget to None, or Qt will
        # complain if a widget is already set on the window.
        self.widget().setWidget(None)
        self.widget().setWidget(widget)
        # On OSX, the resize gripper will be obscured unless we
        # lower the widget in the window's stacking order.
        widget.lower()

