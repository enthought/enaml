import wx

from traits.api import Instance
from traitsui.ui import UI

from .wx_element import WXElement

from ..traitsui_item import ITraitsUIItemImpl


class WXTraitsUIItem(WXElement):

    implements(ITraitsUIItemImpl)
    
    #---------------------------------------------------------------------------
    # ITraitsUIItemImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        parent = self.parent
        model = parent.model
        view = parent.view
        handler = parent.handler
        parent_widget = self.parent_widget()
        self.ui = ui = model.edit_traits(parent=parent_widget, view=view,
                                         handler=handler, kind='subpanel')
        self.widget = ui.control
    
    def inititialize_widget(self):
        pass
        
    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    ui = Instance(UI)

