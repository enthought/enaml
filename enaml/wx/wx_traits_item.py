import wx

from .wx_control import WxControl


class WxTraitsItem(WxControl):
    """ A Wx implementation of an Enaml TraitsUIItem.

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
        # if parent is a main window, we need to ensure proper sizing
        if hasattr(parent, 'SetCentralWidget'):
            size = ui.control.GetSize()
            ui.control.SetMinSize(size)
            parent.SetMinSize(size)
            parent.SetSize(size)
        return ui.control

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(WxTraitsItem, self).create(tree)

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