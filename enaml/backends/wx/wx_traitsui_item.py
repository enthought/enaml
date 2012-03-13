#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_control import WXControl

from ...components.traitsui_item import AbstractTkTraitsUIItem


class WXTraitsUIItem(WXControl, AbstractTkTraitsUIItem):
    """ A wxPython implementation of TraitsUIItem.

    The traits ui item allows the embedding of a traits ui window in
    an Enaml application.

    See Also
    --------
    TraitsUIItem

    """
    ui = None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying traits ui subpanel.

        """
        shell = self.shell_obj
        model = shell.model
        view = shell.view
        handler = shell.handler
        self.ui = ui = model.edit_traits(parent=parent, view=view,
                                         handler=handler, kind='subpanel')
        self.widget = ui.control

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_model_changed(self, model):
        raise NotImplementedError

    def shell_view_changed(self, view):
        raise NotImplementedError

    def shell_handler_changed(self, handler):
        raise NotImplementedError

