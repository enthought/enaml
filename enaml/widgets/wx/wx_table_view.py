import wx.grid

from traits.api import implements, Instance

from .wx_control import WXControl

from ..table_view import ITableViewImpl

from ...item_models.abstract_item_model import ModelIndex, DISPLAY_ROLE, VERTICAL, HORIZONTAL


class AbstractItemModelWrapper(wx.grid.PyGridTableBase):

    def __init__(self, item_model):
        super(AbstractItemModelWrapper, self).__init__()
        self._item_model = item_model
        self._item_model.on_trait_change(self._refresh_table, 'data_changed')
    
    def _refresh_table(self):
        self.Clear()
        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.GetView().ProcessTableMessage(msg)
        self.GetView().Refresh()

    def GetNumberRows(self):
        return self._item_model.row_count()
    
    def GetNumberCols(self):
        return self._item_model.column_count()
    
    def GetValue(self, row, col, parent_index=ModelIndex()):
        model = self._item_model
        index = model.index(row, col, parent_index)
        return self._item_model.data(index, DISPLAY_ROLE)

    def GetRowLabelValue(self, row):
        model = self._item_model
        return model.header_data(row, VERTICAL, DISPLAY_ROLE)

    def GetColLabelValue(self, col):
        model = self._item_model
        return model.header_data(col, HORIZONTAL, DISPLAY_ROLE)


class WXTableView(WXControl):

    implements(ITableViewImpl)

    model_wrapper = Instance(AbstractItemModelWrapper)

    #---------------------------------------------------------------------------
    # ITableViewImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        self.widget = widget = wx.grid.Grid(self.parent_widget())
        widget.SetDoubleBuffered(True)

    def initialize_widget(self):
        model_wrapper = AbstractItemModelWrapper(self.parent.item_model)
        self.widget.SetTable(model_wrapper)
        self.model_wrapper = model_wrapper

    def create_style_handler(self):
        pass
    
    def initialize_style(self):
        style = self.parent.style
        min_width = style.get_property("min_width")
        min_height = style.get_property("min_height")

        if isinstance(min_width, int) and min_width >= 0:
            pass
        else:
            min_width = -1

        if isinstance(min_height, int) and min_height >= 0:
            pass
        else:
            min_height = -1

        self.widget.SetMinSize((min_width, min_height))

    def parent_item_model_changed(self, item_model):
        pass
    
    #---------------------------------------------------------------------------
    # implementation
    #---------------------------------------------------------------------------
    
