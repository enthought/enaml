import wx

from traits.api import implements, on_trait_change

from .wx_container import WXContainer

from ..form import IFormImpl


class WXForm(WXContainer):

    implements(IFormImpl)

    def create_widget(self):
        self.widget = wx.FlexGridSizer()

    def initialize_widget(self):
        pass
    
    def layout_child_widgets(self):
        sizer = self.widget
        sizer.SetCols(2)
        sizer.SetHGap(12)
        sizer.AddGrowableCol(1, 1)
        sizer.SetFlexibleDirection(wx.HORIZONTAL)
        parent_widget = self.parent_widget()
        for child in self.parent.children:
            label = wx.StaticText(parent_widget)
            label.SetLabel(child.name)
            child_widget = child.toolkit_widget()
            sizer.Add(label)
            sizer.Add(child_widget, 1, wx.EXPAND)
    
    @on_trait_change('parent:children:name')
    def update_names(self, obj, name, old, new):
        sizer = self.widget
        control = obj.toolkit_widget()
        sizer_item = sizer.GetItem(control)
        if sizer_item:
            sizer_items = sizer.GetChildren()
            idx = sizer_items.index(sizer_item)
            item = sizer_items[idx - 1]
            label = item.GetWindow()
            label.SetLabel(new)
            sizer.Layout()

