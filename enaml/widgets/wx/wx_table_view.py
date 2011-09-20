#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx.grid

from traits.api import implements, Instance

from .wx_control import WXControl
from .styling import wx_color_from_color

from ..table_view import ITableViewImpl

from ...item_models.abstract_item_model import AbstractItemModel, ModelIndex
from ...enums import DataRole, Orientation


# XXX we need to add more handler support for the different modes of 
# resetting the grid.
class AbstractItemModelTable(wx.grid.PyGridTableBase):

    def __init__(self, item_model):
        super(AbstractItemModelTable, self).__init__()
        if not isinstance(item_model, AbstractItemModel):
            raise TypeError('Model must be an instance of AbstractItemModel.')
        self._item_model = item_model
        self._item_model.on_trait_change(self._end_model_reset, 'model_reset')
        self._item_model.on_trait_change(self._data_changed, 'data_changed')

    def _end_model_reset(self):
        grid = self.GetView()
        grid.SetTable(self)
        grid.Refresh()

    def _data_changed(self):
        grid = self.GetView()
        flag = wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES
        msg = wx.grid.GridTableMessage(self, flag)
        grid.ProcessTableMessage(msg)
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
        if bgcolor:
            attr.SetBackgroundColour(wx_color_from_color(bgcolor))

        fgcolor = model.data(index, DataRole.FOREGROUND)
        if fgcolor:
            attr.SetTextColour(wx_color_from_color(fgcolor))

        return attr

    def GetRowLabelValue(self, row):
        model = self._item_model
        return model.header_data(row, Orientation.VERTICAL, DataRole.DISPLAY)

    def GetColLabelValue(self, col):
        model = self._item_model
        return model.header_data(col, Orientation.HORIZONTAL, DataRole.DISPLAY)


class WXTableView(WXControl):
    """ A wxPython implementation of TableView.
    
    See Also
    --------
    TableView
    
    """
    implements(ITableViewImpl)

    #: The underlying model.
    model_wrapper = Instance(AbstractItemModelTable)

    #---------------------------------------------------------------------------
    # ITableViewImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying wx.grid.Grid control.
        
        """
        self.widget = widget = wx.grid.Grid(self.parent_widget())
        widget.SetDoubleBuffered(True)

    def initialize_widget(self):
        """ Intialize the widget with the attributes of this instance.
        
        """
        self.set_table_model(self.parent.item_model)
        self.bind()

    def create_style_handler(self):
        """ Initialize a style handler.
        
        """
        pass
    
    def initialize_style(self):
        """ Configure the widget's minimum width and height.
        
        """
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
        """ The change handler for the 'item_model' attribute. Not meant
        for public consumption.
        
        """
        self.set_table_model(item_model)
        
    #---------------------------------------------------------------------------
    # implementation
    #---------------------------------------------------------------------------
    def bind(self):
        """ Bind the event handlers for the table view. Not meant for
        public consumption.

        """
        widget = self.widget
        widget.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_select_cell)
        widget.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_left_dclick)
    
    def on_select_cell(self, event):
        """ The event handler for the cell selection event.  Not meant
        for public consumption.

        """
        event.Skip()
        parent = self.parent
        parent_index = ModelIndex()
        row = event.GetRow()
        col = event.GetCol()
        index = parent.item_model.index(row, col, parent_index)
        parent.selected = index
        

    def on_left_dclick(self, event):
        """ The event handler for the double-click event.  Not meant
        for public consumption.

        """
        event.Skip()
        self.parent.left_dclick = self.parent.selected
        
    def set_table_model(self, model):
        """ Set the table view's model.  Not meant for public
        consumption.

        """
        model_wrapper = AbstractItemModelTable(model)
        self.widget.SetTable(model_wrapper)
        self.widget.Refresh()
        self.model_wrapper = model_wrapper

