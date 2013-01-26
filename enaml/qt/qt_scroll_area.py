#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt, QEvent, QSize, Signal
from .qt.QtGui import QScrollArea
from .qt_constraints_widget import QtConstraintsWidget
from .qt_container import QtContainer


SCROLLBAR_MAP = {
    'as_needed' : Qt.ScrollBarAsNeeded,
    'always_off' : Qt.ScrollBarAlwaysOff,
    'always_on' : Qt.ScrollBarAlwaysOn
}


class QCustomScrollArea(QScrollArea):
    """ A custom QScrollArea for use with the QtScrollArea.

    This subclass fixes some bugs related to size hints.

    """
    #: A signal emitted when a LayoutRequest event is posted to the
    #: scroll area. This will typically occur when the size hint of
    #: the scroll area is no longer valid.
    layoutRequested = Signal()

    #: A private internally cached size hint.
    _size_hint = QSize()

    def event(self, event):
        """ A custom event handler which handles LayoutRequest events.

        When a LayoutRequest event is posted to this widget, it will
        emit the `layoutRequested` signal. This allows an external
        consumer of this widget to update their external layout.

        """
        res = super(QCustomScrollArea, self).event(event)
        if event.type() == QEvent.LayoutRequest:
            self._size_hint = QSize()
            self.layoutRequested.emit()
        return res

    def setWidget(self, widget):
        """ Set the widget for this scroll area.

        This is a reimplemented parent class method which invalidates
        the cached size hint before setting the widget.

        """
        self._size_hint = QSize()
        self.takeWidget() # Let Python keep ownership of the old widget
        super(QCustomScrollArea, self).setWidget(widget)

    def sizeHint(self):
        """ Get the size hint for the scroll area.

        This reimplemented method fixes a Qt bug where the size hint
        is not updated after the scroll widget is first shown. The
        bug is documented on the Qt bug tracker:
        https://bugreports.qt-project.org/browse/QTBUG-10545

        """
        # This code is ported directly from QScrollArea.cpp but instead
        # of caching the size hint of the scroll widget, it caches the
        # size hint for the entire scroll area, and invalidates it when
        # the widget is changed or it receives a LayoutRequest event.
        hint = self._size_hint
        if hint.isValid():
            return QSize(hint)
        fw = 2 * self.frameWidth()
        hint = QSize(fw, fw)
        font_height = self.fontMetrics().height()
        widget = self.widget()
        if widget is not None:
            if self.widgetResizable():
                hint += widget.sizeHint()
            else:
                hint += widget.size()
        else:
            hint += QSize(12 * font_height, 8 * font_height)
        if self.verticalScrollBarPolicy() == Qt.ScrollBarAlwaysOn:
            vbar = self.verticalScrollBar()
            hint.setWidth(hint.width() + vbar.sizeHint().width())
        if self.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOn:
            hbar = self.horizontalScrollBar()
            hint.setHeight(hint.height() + hbar.sizeHint().height())
        hint = hint.boundedTo(QSize(36 * font_height, 24 * font_height))
        self._size_hint = hint
        return QSize(hint)


class QtScrollArea(QtConstraintsWidget):
    """ A Qt implementation of an Enaml ScrollArea.

    """
    #: A private cache of the old size hint for the scroll area.
    _old_hint = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QScrollArea widget.

        """
        return QCustomScrollArea(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtScrollArea, self).create(tree)
        self.set_horizontal_policy(tree['horizontal_policy'])
        self.set_vertical_policy(tree['vertical_policy'])
        self.set_widget_resizable(tree['widget_resizable'])

    def init_layout(self):
        """ Initialize the layout of the underlying widget.

        """
        super(QtScrollArea, self).init_layout()
        widget = self.widget()
        widget.setWidget(self.scroll_widget())
        widget.layoutRequested.connect(self.on_layout_requested)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def scroll_widget(self):
        """ Find and return the scroll widget child for this widget.

        Returns
        -------
        result : QWidget or None
            The scroll widget defined for this widget, or None if one is
            not defined.

        """
        widget = None
        for child in self.children():
            if isinstance(child, QtContainer):
                widget = child.widget()
        return widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtScrollArea.

        """
        if isinstance(child, QtContainer):
            self.widget().setWidget(self.scroll_widget())

    def child_added(self, child):
        """ Handle the child added event for a QtScrollArea.

        """
        if isinstance(child, QtContainer):
            self.widget().setWidget(self.scroll_widget())

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_layout_requested(self):
        """ Handle the `layoutRequested` signal from the QScrollArea.

        """
        new_hint = self.widget().sizeHint()
        if new_hint != self._old_hint:
            self._old_hint = new_hint
            self.size_hint_updated()

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def replace_constraints(self, old_cns, new_cns):
        """ A reimplemented QtConstraintsWidget layout method.

        Constraints layout may not cross the boundary of a ScrollArea,
        so this method is no-op which stops the layout propagation.

        """
        pass

    def clear_constraints(self, cns):
        """ A reimplemented QtConstraintsWidget layout method.

        Constraints layout may not cross the boundary of a ScrollArea,
        so this method is no-op which stops the layout propagation.

        """
        pass

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_horizontal_policy(self, content):
        """ Handle the 'set_horizontal_policy' action from the Enaml
        widget.

        """
        self.set_horizontal_policy(content['horizontal_policy'])

    def on_action_set_vertical_policy(self, content):
        """ Handle the 'set_vertical_policy' action from the Enaml
        widget.

        """
        self.set_vertical_policy(content['vertical_policy'])

    def on_action_set_widget_resizable(self, content):
        """ Handle the 'set_widget_resizable' action from the Enaml
        widget.

        """
        self.set_widget_resizable(content['widget_resizable'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_horizontal_policy(self, policy):
        """ Set the horizontal scrollbar policy of the widget.

        """
        self.widget().setHorizontalScrollBarPolicy(SCROLLBAR_MAP[policy])

    def set_vertical_policy(self, policy):
        """ Set the vertical scrollbar policy of the widget.

        """
        self.widget().setVerticalScrollBarPolicy(SCROLLBAR_MAP[policy])

    def set_widget_resizable(self, resizable):
        """ Set whether or not the scroll widget is resizable.

        """
        self.widget().setWidgetResizable(resizable)

