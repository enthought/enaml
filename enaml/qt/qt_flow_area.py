#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QScrollArea, QFrame
from .qt_constraints_widget import QtConstraintsWidget
from .qt_flow_item import QtFlowItem
from .q_flow_layout import QFlowLayout


_DIRECTION_MAP = {
    'left_to_right': QFlowLayout.LeftToRight,
    'right_to_left': QFlowLayout.RightToLeft,
    'top_to_bottom': QFlowLayout.TopToBottom,
    'bottom_to_top': QFlowLayout.BottomToTop,
}


_ALIGN_MAP = {
    'leading': QFlowLayout.AlignLeading,
    'trailing': QFlowLayout.AlignTrailing,
    'center': QFlowLayout.AlignCenter,
    'justify': QFlowLayout.AlignJustify,
}


class QFlowArea(QScrollArea):

    def __init__(self, *args, **kwargs):
        super(QFlowArea, self).__init__(*args, **kwargs)
        self.setWidgetResizable(True)
        self._area_widget = QFrame(self)
        self._area_layout = QFlowLayout()
        self._area_widget.setLayout(self._area_layout)
        self.setWidget(self._area_widget)

    def addWidget(self, widget):
        self._area_layout.addWidget(widget)

    def insertWidget(self, index, widget):
        self._area_layout.insertWidget(index, widget)

    def margins(self):
        return self._area_layout.getContentsMargins()

    def setMargins(self, left, top, right, bottom):
        self._area_layout.setContentsMargins(left, top, right, bottom)

    def aligment(self):
        return self._area_layout.alignment()

    def setAlignment(self, alignment):
        self._area_layout.setAlignment(alignment)

    def direction(self):
        return self._area_layout.direction()

    def setDirection(self, direction):
        self._area_layout.setDirection(direction)

    def verticalSpacing(self):
        return self._area_layout.verticalSpacing()

    def setVerticalSpacing(self, spacing):
        self._area_layout.setVerticalSpacing(spacing)

    def horizontalSpacing(self):
        return self._area_layout.horizontalSpacing()

    def setHorizontalSpacing(self, spacing):
        self._area_layout.setHorizontalSpacing(spacing)


class QtFlowArea(QtConstraintsWidget):
    """ A Qt implementation of an Enaml FlowArea.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying widget.

        """
        return QFlowArea(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtFlowArea, self).create(tree)
        self.set_direction(tree['direction'])
        self.set_align(tree['align'])
        self.set_horizontal_spacing(tree['horizontal_spacing'])
        self.set_vertical_spacing(tree['vertical_spacing'])
        self.set_margins(tree['margins'])

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtFlowArea, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtFlowItem):
                widget.addWidget(child.widget())

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtMdiArea.

        """
        # if isinstance(child, QtMdiWindow):
        #     self.widget().removeSubWindow(child.widget())

    def child_added(self, child):
        """ Handle the child added event for a QtMdiArea.

        """
        # The size hint of a QMdiArea is typically quite large and the
        # size hint constraints are usually ignored. There is no need
        # to notify of a change in size hint here.
        # if isinstance(child, QtMdiWindow):
        #     self.widget().addSubWindow(child.widget())

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_direction(self, content):
        """ Handle the 'set_direction' action from the Enaml widget.

        """
        self.set_direction(content['direction'])

    def on_action_set_align(self, content):
        """ Handle the 'set_align' action from the Enaml widget.

        """
        self.set_align(content['align'])

    def on_action_set_horizontal_spacing(self, content):
        """ Handle the 'set_horizontal_spacing' action from the Enaml
        widget.

        """
        self.set_horizontal_spacing(content['horizontal_spacing'])

    def on_action_set_vertical_spacing(self, content):
        """ Handle the 'set_vertical_spacing' action from the Enaml
        widget.

        """
        self.set_vertical_spacing(content['vertical_spacing'])

    def on_action_set_margins(self, content):
        """ Handle the 'set_margins' action from the Enaml widget.

        """
        self.set_margins(content['margins'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_direction(self, direction):
        """ Set the direction for the underlying control.

        """
        self.widget().setDirection(_DIRECTION_MAP[direction])

    def set_align(self, align):
        """ Set the alignment for the underlying control.

        """
        self.widget().setAlignment(_ALIGN_MAP[align])

    def set_horizontal_spacing(self, spacing):
        """ Set the horizontal spacing of the underyling control.

        """
        self.widget().setHorizontalSpacing(spacing)

    def set_vertical_spacing(self, spacing):
        """ Set the vertical spacing of the underlying control.

        """
        self.widget().setVerticalSpacing(spacing)

    def set_margins(self, margins):
        """ Set the margins of the underlying control.

        """
        top, right, bottom, left = margins
        self.widget().setMargins(left, top, right, bottom)

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def replace_constraints(self, old_cns, new_cns):
        """ A reimplemented QtConstraintsWidget layout method.

        Constraints layout may not cross the boundary of a ScrollArea,
        so this method is no-op which stops the layout propagation.

        """
        pass

