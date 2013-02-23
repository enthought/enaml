#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#
#------------------------------------------------------------------------------
from enaml.qt.qt.QtGui import QFrame
from enaml.qt.q_single_widget_layout import QSingleWidgetLayout
from enaml.qt.qt_constraints_widget import size_hint_guard
from enaml.qt.qt_control import QtControl


class QtEmbedWidget(QtControl):
    """ A Qt implementation of an Enaml TraitsItem.

    """
    #: Internal storage for the Qt widget
    _embedded_widget = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying widget.

        """
        widget = QFrame(parent)
        layout = QSingleWidgetLayout()
        widget.setLayout(layout)
        return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtEmbedWidget, self).create(tree)
        self._embedded_widget = tree['widget']

    def init_layout(self):
        """ Initialize the layout for the widget.

        """
        super(QtEmbedWidget, self).init_layout()
        self.refresh_qt_widget()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_widget(self, content):
        """ Handle the 'set_model' action from the Enaml widget.

        """
        self._embedded_widget = content['widget']
        with size_hint_guard(self):
            self.refresh_qt_widget()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def refresh_qt_widget(self):
        """ Create the Qt widget and update the underlying control.

        """
        self.widget().layout().setWidget(self._embedded_widget)

