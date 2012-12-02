from .qt.QtCore import Qt, QMargins
from .qt.QtGui import QWidget, QVBoxLayout
from .qt_control import QtControl


class QtTraitsUIItem(QtControl):
    """ A Qt implementation of an Enaml TraitsUIItem.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying label widget.

        """
        model = tree['model']
        ui = model.edit_traits(parent=parent, view=tree['view'],
                    handler=tree['handler'], kind='subpanel')
        # on qt, we must set this explicitly
        ui.control.setParent(parent)
        # if parent is a main window, we need to ensure proper sizing
        if hasattr(parent, 'centralWidget'):
            size = ui.control.sizeHint()
            ui.control.setMinimumSize(size)
            parent.setMinimumSize(size)
        return ui.control

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtTraitsUIItem, self).create(tree)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_model(self, content):
        """ Handle the 'set_model' action from the Enaml widget.

        """
        raise NotImplementedError

    def on_action_set_handler(self, content):
        """ Handle the 'set_handler' action from the Enaml widget.

        """
        raise NotImplementedError

    def on_action_set_view(self, content):
        """ Handle the 'set_view' action from the Enaml widget.

        """
        raise NotImplementedError
    '''
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_model(self, model):
        """ Set the model for the underlying widget.

        """
        self.model = model

    def set_handler(self, handler):
        """ Set the handler for the underlying widget.

        """
        self.handler = handler

    def set_view(self, view):
        """ Set the view in the underlying widget.

        """
        self.view = view
        widget = self.widget()
        # support changing views
        layout = widget.layout()
        if not layout:
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(QMargins(0, 0, 0, 0))
        else:
            layout.removeWidget(self.ui.control)
            self.ui.control.hide()
        # create the view and add it to our layout
        self.ui = ui = self.model.edit_traits(parent=widget, view=view,
                                    handler=self.handler, kind='subpanel')
        layout.addWidget(ui.control)
        # TraitsUI doesn't properly set the parent on Qt
        ui.control.setParent(widget)
        # make sure the widget scales appropriately
        # (especially when view changes)
        size = ui.control.sizeHint()
        self.set_minimum_size((size.width(), size.height()))
        self.size_hint_updated()
        parent = self.parent()

    '''