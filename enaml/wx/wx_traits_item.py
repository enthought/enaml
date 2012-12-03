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
	widget = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
	vbox = wx.BoxSizer(wx.VERTICAL)
	widget.SetSizer(vbox)
	return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(WxTraitsItem, self).create(tree)
	self.model = tree['model']
	self.view = tree['view']
	self.handler = tree['handler']
	self.ui = None

    def init_layout(self):
        '''Create the Traits UI widget and add to our layout
        '''
	super(WxTraitsItem, self).init_layout()
        # guard against using a named view that is not supported by the model
	if isinstance(self.view, (str, unicode)):
	    if self.model.trait_view(self.view) is None:
		self.view = ''
        # remove any previous widget before adding a new one
        if self.ui:
	    self.widget().GetSizer().Remove(self.ui.control)
	    self.ui.control.Hide()
        self.ui = self.model.edit_traits(parent=self.widget(), view=self.view,
                    handler=self.handler, kind='subpanel')
        self.widget().GetSizer().Add(self.ui.control, 1,
	                             wx.LEFT | wx.TOP | wx.GROW)
	# allow the widget to resize when the view is changed
	size = self.ui.control.GetSize()
	self.set_minimum_size((size.width, size.height))
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
	self.init_layout()

    def on_action_set_view(self, content):
        """ Handle the 'set_view' action from the Enaml widget.

        """
        self.view = content['view']
        self.init_layout()