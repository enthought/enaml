from .qt.QtCore import Qt, QMargins
from .qt.QtGui import QWidget, QVBoxLayout, QFrame
from .qt_control import QtControl


class QtTraitsItem(QtControl):
    """ A Qt implementation of an Enaml TraitsItem.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying label widget.

        """
        widget = QFrame(parent)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtTraitsItem, self).create(tree)
        self.model = tree['model']
        self.view = tree['view']
        self.handler = tree['handler']
        self.ui = None

    def init_layout(self):
        '''Create the Traits UI widget and add to our layout
        '''
        # guard against using a view that is not supported by the model
        if not self.model.trait_view(self.view):
            self.view = ''
        # remove any previous widget before adding a new one
        if self.ui:
            self.widget().layout().removeWidget(self.ui.control)
            self.ui.control.hide()
        self.ui = self.model.edit_traits(parent=self.widget(), view=self.view,
                    handler=self.handler, kind='subpanel')
        # on qt, we must set this explicitly
        self.ui.control.setParent(self.widget())
        self.widget().layout().addWidget(self.ui.control)
	size = self.ui.control.sizeHint()
	self.set_minimum_size((size.width(), size.height()))
	self.size_hint_updated()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_model(self, content):
        """ Handle the 'set_model' action from the Enaml widget.

        """
        self.model = content['model']
        self.init_layout()

    def on_action_set_handler(self, content):
        """ Handle the 'set_handler' action from the Enaml widget.

        """
        self.handler = content['handler']

    def on_action_set_view(self, content):
        """ Handle the 'set_view' action from the Enaml widget.

        """
        self.view = content['view']
        self.init_layout()