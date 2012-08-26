#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QMdiSubWindow, QLayout
from .qt_widget_component import QtWidgetComponent


class QtMdiWindow(QtWidgetComponent):
    """ A Qt implementation of an Enaml MdiWindow.

    """
    #: Storage for the mdi widget id.
    _mdi_widget_id = None

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

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtMdiWindow, self).create(tree)
        self.set_mdi_widget_id(tree['mdi_widget_id'])

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtMdiWindow, self).init_layout()
        child = self.find_child(self._mdi_widget_id)
        if child is not None:
            # We need to unparent the underlying widget before adding 
            # it to the subwindow. Otherwise, children like QMainWindow
            # will persist as top-level non-mdi widgets.
            child_widget = child.widget()
            child_widget.setParent(None)
            self.widget().setWidget(child_widget)
            # On OSX, the resize gripper will be obscured unless we
            # lower the widget in the window's stacking order.
            child_widget.lower()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_mdi_widget_id(self, widget_id):
        """ Set the widget id for the mdi widget.

        """
        self._mdi_widget_id = widget_id

