import wx

from traits.api import Instance, HasTraits, Any
from traitsui.api import View, Handler
from traitsui.ui import UI

from .wx_element import WXElement


class WXTraitsUIItem(WXElement):

    # The HasTraits object that will provide the traits ui view
    model = Instance(HasTraits)

    # The traits view for editing the object. Optional.
    view = Instance(View)

    # The handler for editing the object. Optional.
    handler = Instance(Handler)
    
    # The UI instance for the view we are embedding.
    ui_item = Instance(UI)
    
    def create_widget(self):
        self.widget = wx.Panel(self.parent_widget())
    
    def init_attributes(self):
        widget = self.widget

        ui_item = self.model.edit_traits(parent=widget, view=self.view,
                handler=self.handler, kind='subpanel')
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(ui_item.control)
        self.widget.SetSizer(vbox)
        self.widget.Show()
        
        self.ui_item = ui_item
    
    def init_meta_handlers(self):
        pass

        
    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _model_changed(self):
        self.layout_children()

    def _view_changed(self):
        self.layout_children()

    def _handler_changed(self):
        self.layout_children()


