import wx.grid

from traits.api import implements, Instance

from .wx_control import WXControl
from .styling import wx_color_from_color

from ..table_view import ITableViewImpl

from ...item_models.abstract_item_model import ModelIndex
from ...enums import DataRole, Orientation


# XXX we need to add more handler support for the different modes of 
# resetting the grid.
class AbstractItemModelTable(wx.grid.PyGridTableBase):

    def __init__(self, item_model):
        super(AbstractItemModelTable, self).__init__()
        self._item_model = item_model
        self._item_model.on_trait_change(self._end_model_reset, 'model_reset')

    def _end_model_reset(self):
        grid = self.GetView()
        grid.SetTable(self)
        grid.Refresh()

    def GetNumberRows(self):
        return self._item_model.row_count()
    
    def GetNumberCols(self):
        return self._item_model.column_count()
    
    def GetValue(self, row, col, parent_index=ModelIndex()):
        model = self._item_model
        index = model.index(row, col, parent_index)
        return model.data(index, DataRole.DISPLAY)

    def GetAttr(self, row, col, ignored, parent_index=ModelIndex()):
        model = self._item_model
        index = model.index(row, col, parent_index)

        attr = wx.grid.GridCellAttr()

        bgcolor = model.data(index, DataRole.BACKGROUND)
        attr.SetBackgroundColour(wx_color_from_color(bgcolor))

        fgcolor = model.data(index, DataRole.FOREGROUND)
        attr.SetTextColour(wx_color_from_color(fgcolor))

        return attr

    def GetRowLabelValue(self, row):
        model = self._item_model
        return model.header_data(row, Orientation.VERTICAL, DataRole.DISPLAY)

    def GetColLabelValue(self, col):
        model = self._item_model
        return model.header_data(col, Orientation.HORIZONTAL, DataRole.DISPLAY)


class WXTableView(WXControl):

    implements(ITableViewImpl)

    model_wrapper = Instance(AbstractItemModelTable)

    #---------------------------------------------------------------------------
    # ITableViewImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        self.widget = widget = wx.grid.Grid(self.parent_widget())
        widget.SetDoubleBuffered(True)

    def initialize_widget(self):
        model_wrapper = AbstractItemModelTable(self.parent.item_model)
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
    
