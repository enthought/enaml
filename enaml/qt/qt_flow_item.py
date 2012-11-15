#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt, QSize
from .qt.QtGui import QFrame, QLayout
from .q_flow_layout import QFlowLayout, AbstractFlowWidget, FlowLayoutData
from .q_single_widget_layout import QSingleWidgetLayout
from .qt_container import QtContainer
from .qt_widget_component import QtWidgetComponent


_ALIGN_MAP = {
    'leading': QFlowLayout.AlignLeading,
    'trailing': QFlowLayout.AlignTrailing,
    'center': QFlowLayout.AlignCenter,
}


class QFlowItem(QFrame):
    """ A QFrame subclass which acts as an item in a QFlowArea.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a QFlowItem.

        Parameters
        ----------
        *args, **kwargs
            The position and keyword arguments required to initialize
            a QFrame.

        """
        super(QFlowItem, self).__init__(*args, **kwargs)
        self._flow_widget = None
        self._layout_data = FlowLayoutData()
        self.setLayout(QSingleWidgetLayout())
        self.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)

    def layoutData(self):
        return self._layout_data

    def preferredSize(self):
        return self._layout_data.preferred_size

    def setPreferredSize(self, size):
        d = self._layout_data
        d.preferred_size = size
        d.dirty = True
        self.updateGeometry()

    def alignment(self):
        return self._layout_data.alignment

    def setAlignment(self, alignment):
        d = self._layout_data
        d.alignment = alignment
        d.dirty = True
        self.updateGeometry()

    def stretch(self):
        return self._layout_data.stretch

    def setStretch(self, stretch):
        d = self._layout_data
        d.stretch = stretch
        d.dirty = True
        self.updateGeometry()

    def orthoStretch(self):
        return self._layout_data.stretch

    def setOrthoStretch(self, stretch):
        d = self._layout_data
        d.ortho_stretch = stretch
        d.dirty = True
        self.updateGeometry()

    def flowWidget(self):
        """ Get the flow widget for this flow item.

        Returns
        -------
        result : QWidget or None
            The flow widget being managed by this item.

        """
        return self._flow_widget

    def setFlowWidget(self, widget):
        """ Set the flow widget for this flow item.

        Parameters
        ----------
        widget : QWidget
            The QWidget to use as the flow widget in this item.

        """
        self._flow_widget = widget
        self.layout().setWidget(widget)


AbstractFlowWidget.register(QFlowItem)


class QtFlowItem(QtWidgetComponent):
    """ A Qt implementation of an Enaml FlowItem.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QFlowItem widget.

        """
        return QFlowItem(parent)

    def create(self, tree):
        super(QtFlowItem, self).create(tree)
        self.set_preferred_size(tree['preferred_size'])
        self.set_align(tree['align'])
        self.set_stretch(tree['stretch'])
        self.set_ortho_stretch(tree['ortho_stretch'])

    def init_layout(self):
        """ Initialize the layout for the underyling widget.

        """
        super(QtFlowItem, self).init_layout()
        self.widget().setFlowWidget(self.flow_widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def flow_widget(self):
        """ Find and return the flow widget child for this widget.

        Returns
        -------
        result : QWidget or None
            The flow widget defined for this widget, or None if one is
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
        """ Handle the child added event for a QtFlowItem.

        """
        if isinstance(child, QtContainer):
            self.widget().setFlowWidget(self.flow_widget())

    def child_added(self, child):
        """ Handle the child added event for a QtFlowItem.

        """
        if isinstance(child, QtContainer):
            self.widget().setFlowWidget(self.flow_widget())

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_preferred_size(self, content):
        self.set_preferred_size(content['preferred_size'])

    def on_action_set_align(self, content):
        self.set_align(content['align'])

    def on_action_set_stretch(self, content):
        self.set_stretch(content['stretch'])

    def on_action_set_ortho_stretch(self, content):
        self.set_ortho_stretch(content['ortho_stretch'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_preferred_size(self, size):
        self.widget().setPreferredSize(QSize(*size))

    def set_align(self, align):
        self.widget().setAlignment(_ALIGN_MAP[align])

    def set_stretch(self, stretch):
        self.widget().setStretch(stretch)

    def set_ortho_stretch(self, stretch):
        self.widget().setOrthoStretch(stretch)

