import wx

from traits.api import Instance, Any
from traitsui.ui import UI

from .wx_element import WXElement


class WXTraitsUIItem(WXElement):

    # The HasTraits object that will provide the traits ui view
    model = Any

    # The traits view for editing the object. Optional.
    view = Any

    # The handler for editing the object. Optional.
    handler = Any
    
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


