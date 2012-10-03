#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
import sys

from .qt.QtCore import Qt, QEvent, Signal
from .qt.QtGui import QSplitter
from .qt_constraints_widget import QtConstraintsWidget
from .qt_split_item import QtSplitItem


_ORIENTATION_MAP = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical,
}


class QCustomSplitter(QSplitter):
    """ A custom QSplitter which handles children of type QSplitItem.

    """
    #: A signal emitted when a LayoutRequest event is posted to the
    #: splitter widget. This will typically occur when the size hint
    #: of the splitter is no longer valid.
    layoutRequested = Signal()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def event(self, event):
        """ A custom event handler which handles LayoutRequest events.

        When a LayoutRequest event is posted to this widget, it will
        emit the `layoutRequested` signal. This allows an external
        consumer of this widget to update their external layout.

        """
        res = super(QCustomSplitter, self).event(event)
        if event.type() == QEvent.LayoutRequest:
            self.layoutRequested.emit()
        return res


class QtSplitter(QtConstraintsWidget):
    """ A Qt implementation of an Enaml Splitter.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying QSplitter control.

        """
        return QCustomSplitter(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtSplitter, self).create(tree)
        self.set_orientation(tree['orientation'])
        self.set_live_drag(tree['live_drag'])

    def init_layout(self):
        """ Handle the layout initialization for the splitter.

        """
        super(QtSplitter, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtSplitItem):
                widget.addWidget(child.widget())
        widget.layoutRequested.connect(self.on_layout_requested)

        # On Windows, messages are consumed from three different queues,
        # each with a different priority. The lowest priority is the
        # queue which holds WM_PAINT messages. Dragging the splitter bar
        # generates WM_MOUSEMOVE messages which have a higher priority.
        # These messages (dragging the bar) generate size events in Qt
        # which are delivered immediately. This means that if handling
        # the resize event from the drag takes too long (> ~800us) then 
        # another size event will arrive before the paint event, since
        # the new WM_MOUSEMOVE will be processed before the WM_PAINT.
        # So on Windows, the `splitterMoved` signal, which is emitted 
        # on every drag, is connected to a handler which will force a 
        # repaint if opaque resize is turned on. Since paint event are
        # collapsed, the effect of this is to restore the order of event
        # processing.
        if sys.platform == 'win32':
            widget.splitterMoved.connect(self.on_win32_slider_moved)

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtSplitter.

        """
        if isinstance(child, QtSplitItem):
            self.widget().addWidget(child.widget())

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_layout_requested(self):
        """ Handle the `layoutRequested` signal from the QSplitter.

        """
        self.size_hint_updated()

    def on_win32_slider_moved(self):
        """ Handle the 'sliderMoved' signal from the QSplitter.

        This handler is only connected when running on Windows and it
        serves to make sure paint events get generated during heavy
        resize events when opaque resizing is turned on.

        """
        widget = self.widget()
        if widget.opaqueResize():
            widget.repaint()

    #--------------------------------------------------------------------------
    # Message Handler Methods 
    #--------------------------------------------------------------------------
    def on_action_set_orientation(self, content):
        """ Handle the 'set_orientation' action from the Enaml widget.

        """
        self.set_orientation(content['orientation'])

    def on_action_set_live_drag(self, content):
        """ Handle the 'set_live_drag' action from the Enaml widget.

        """
        self.set_live_drag(content['live_drag'])

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_orientation(self, orientation):
        """ Update the orientation of the QSplitter.

        """
        q_orientation = _ORIENTATION_MAP[orientation]
        self.widget().setOrientation(q_orientation)

    def set_live_drag(self, live_drag):
        """ Update the dragging mode of the QSplitter.

        """
        self.widget().setOpaqueResize(live_drag)

    # def set_preferred_sizes(self, sizes):
    #     """ Set the preferred sizes for the children.

    #     For sizes not supplied by the user, either via None values or 
    #     a list which is too short, the current size for that element
    #     will be used in its place.

    #     """
    #     widget = self.widget()
    #     curr_sizes = widget.sizes()[:]
    #     max_idx = min(len(curr_sizes), len(sizes))
    #     for idx in xrange(max_idx):
    #         size = sizes[idx]
    #         if size is not None:
    #             curr_sizes[idx] = size
    #     widget.setSizes(curr_sizes)

