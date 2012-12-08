#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#
# Special thanks to Steven Silvester for contributing this module!
#------------------------------------------------------------------------------
import wx

from .wx_control import WxControl
from .wx_single_widget_sizer import wxSingleWidgetSizer


class WxTraitsItem(WxControl):
    """ A Wx implementation of an Enaml TraitsItem.

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
        widget = wx.Panel(parent)
        sizer = wxSingleWidgetSizer()
        widget.SetSizer(sizer)
        return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(WxTraitsItem, self).create(tree)
        self._model = tree['model']
        self._view = tree['view']
        self._handler = tree['handler']

    def init_layout(self):
        """ Initialize the layout for the widget.

        """
        super(WxTraitsItem, self).init_layout()
        self.refresh_traits_widget(notify=False)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_model(self, content):
        """ Handle the 'set_model' action from the Enaml widget.

        """
        self._model = content['model']
        self.refresh_traits_widget()

    def on_action_set_view(self, content):
        """ Handle the 'set_view' action from the Enaml widget.

        """
        self._view = content['view']
        self.refresh_traits_widget()

    def on_action_set_handler(self, content):
        """ Handle the 'set_handler' action from the Enaml widget.

        """
        self._handler = content['handler']
        self.refresh_traits_widget()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def refresh_traits_widget(self, notify=True):
        """ Create the traits widget and update the underlying control.

        Parameters
        ----------
        notify : bool, optional
            Whether to notify the layout system if the size hint of the
            widget has changed. The default is True.

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
        if notify:
            old_hint = widget.GetBestSize()
            widget.GetSizer().Add(control)
            new_hint = widget.GetBestSize()
            if old_hint != new_hint:
               self.size_hint_updated()
        else:
            widget.GetSizer().Add(control)

