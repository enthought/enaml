#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#
# Special thanks to Steven Silvester for contributing this module!
#------------------------------------------------------------------------------
from .qt.QtGui import QFrame
from .q_single_widget_layout import QSingleWidgetLayout
from .qt_constraints_widget import size_hint_guard
from .qt_control import QtControl


class QtTraitsItem(QtControl):
    """ A Qt implementation of an Enaml TraitsItem.

    """
    #: Internal storage for the traits model
    _model = None

    #: Internal storage for the traits view
    _view = None

    #: Internal storage for the traits handler
    _handler = None

    #: Internal storage for the generated traits UI object.
    _ui = None

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
        super(QtTraitsItem, self).create(tree)
        self._model = tree['model']
        self._view = tree['view']
        self._handler = tree['handler']

    def init_layout(self):
        """ Initialize the layout for the widget.

        """
        super(QtTraitsItem, self).init_layout()
        self.refresh_traits_widget()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_model(self, content):
        """ Handle the 'set_model' action from the Enaml widget.

        """
        self._model = content['model']
        with size_hint_guard(self):
            self.refresh_traits_widget()

    def on_action_set_view(self, content):
        """ Handle the 'set_view' action from the Enaml widget.

        """
        self._view = content['view']
        with size_hint_guard(self):
            self.refresh_traits_widget()

    def on_action_set_handler(self, content):
        """ Handle the 'set_handler' action from the Enaml widget.

        """
        self._handler = content['handler']
        with size_hint_guard(self):
            self.refresh_traits_widget()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def refresh_traits_widget(self):
        """ Create the traits widget and update the underlying control.

        """
        widget = self.widget()
        model = self._model
        if model is None:
            control = None
        else:
            view = self._view
            handler = self._handler
            self._ui = ui = model.edit_traits(
                parent=widget, view=view, handler=handler, kind='subpanel',
            )
            control = ui.control
        widget.layout().setWidget(control)

