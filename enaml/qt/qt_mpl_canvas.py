#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#
# Special thanks to Steven Silvester for contributing this module!
#------------------------------------------------------------------------------
from .qt.QtCore import Qt
from .qt.QtGui import QFrame, QVBoxLayout
from .qt_control import QtControl

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg


class QtMPLCanvas(QtControl):
    """ A Qt implementation of an Enaml MPLCanvas.

    """
    #: Internal storage for the matplotlib figure.
    _figure = None

    #: Internal storage for whether or not to show the toolbar.
    _toolbar_visible = False

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying widget.

        """
        widget = QFrame(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        widget.setLayout(layout)
        return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtMPLCanvas, self).create(tree)
        self._figure = tree['figure']
        self._toolbar_visible = tree['toolbar_visible']

    def init_layout(self):
        """ Initialize the layout of the underlying widget.

        """
        super(QtMPLCanvas, self).init_layout()
        self.refresh_mpl_widget(notify=False)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_figure(self, content):
        """ Handle the 'set_figure' action from the Enaml widget.

        """
        self._figure = content['figure']
        self.refresh_mpl_widget()

    def on_action_set_toolbar_visible(self, content):
        """ Handle the 'set_toolbar_visible' action from the Enaml
        widget.

        """
        visible = content['toolbar_visible']
        self._toolbar_visible = visible
        layout = self.widget().layout()
        if layout.count() == 2:
            item = self.widget_item()
            old_hint = item.sizeHint()
            toolbar = layout.itemAt(0).widget()
            toolbar.setVisible(visible)
            new_hint = item.sizeHint()
            if old_hint != new_hint:
                self.size_hint_updated()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def refresh_mpl_widget(self, notify=True):
        """ Create the mpl widget and update the underlying control.

        Parameters
        ----------
        notify : bool, optional
            Whether to notify the layout system if the size hint of the
            widget has changed. The default is True.

        """
        # Delete the old widgets in the layout, it's too much shennigans
        # to try to reuse old widgets. If the size hint event should
        # be emitted, compute the old size hint first.
        widget = self.widget()
        if notify:
            item = self.widget_item()
            old_hint = item.sizeHint()
        layout = widget.layout()
        while layout.count():
            layout_item = layout.takeAt(0)
            layout_item.widget().deleteLater()

        # Create the new figure and toolbar widgets. It seems that key
        # events will not be processed without an mpl figure manager.
        # However, a figure manager will create a new toplevel window,
        # which is certainly not desired in this case. This appears to
        # be a limitation of matplotlib. The canvas is manually set to
        # visible, or QVBoxLayout will ignore it for size hinting.
        figure = self._figure
        if figure is not None:
            canvas = FigureCanvasQTAgg(figure)
            canvas.setParent(widget)
            canvas.setFocusPolicy(Qt.ClickFocus)
            canvas.setVisible(True)
            toolbar = NavigationToolbar2QTAgg(canvas, widget)
            toolbar.setVisible(self._toolbar_visible)
            layout.addWidget(toolbar)
            layout.addWidget(canvas)

        if notify:
            new_hint = item.sizeHint()
            if old_hint != new_hint:
                self.size_hint_updated()

