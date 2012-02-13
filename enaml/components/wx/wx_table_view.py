#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.grid

from .wx_control import WXControl
from ..table_view import AbstractTkTableView

from ...item_models.abstract_item_model import AbstractItemModel, ITEM_IS_EDITABLE


GridCellAttr = wx.grid.GridCellAttr


def wx_color_from_color(color):
    return wx.Color(*color)


# XXX we need to add more handler support for the different modes of
# resetting the grid.
class AbstractItemModelTable(wx.grid.PyGridTableBase):

    def __init__(self, item_model):
        super(AbstractItemModelTable, self).__init__()
        if not isinstance(item_model, AbstractItemModel):
            raise TypeError('Model must be an instance of AbstractItemModel.')
        self._item_model = item_model

        # Cache frequently used bound methods
        self._row_count = item_model.row_count
        self._col_count = item_model.column_count
        self._model_index = item_model.index
        self._model_data = item_model.data
        self._model_background = item_model.background
        self._model_foreground = item_model.foreground
        self._vert_header_data = item_model.vertical_header_data
        self._horiz_header_data = item_model.horizontal_header_data

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
        return self._row_count()

    def GetNumberCols(self):
        return self._col_count()

    def GetValue(self, row, col):
        index = self._model_index(row, col, None)
        return self._model_data(index)

    def GetAttr(self, row, col, ignored):
        index = self._model_index(row, col, None)

        attr = GridCellAttr()

        brush = self._model_background(index)
        if brush is not None:
            attr.SetBackgroundColour(wx_color_from_color(brush.color))

        brush = self._model_foreground(index)
        if brush is not None:
            attr.SetTextColour(wx_color_from_color(brush.color))
            
        return attr

    def SetValue(self, row, col, val):
        item_model = self._item_model
        index = item_model.index(row, col, None)
        flags = item_model.flags(index)
        if flags & ITEM_IS_EDITABLE:
            item_model.set_data(index, val)

    def GetRowLabelValue(self, row):
        return self._vert_header_data(row)

    def GetColLabelValue(self, col):
        return self._horiz_header_data(col)


class WXTableView(WXControl, AbstractTkTableView):
    """ A wxPython implementation of TableView.

    """
    #: The underlying model.
    model_wrapper = None

    #---------------------------------------------------------------------------
    # ITableViewImpl interface
    #---------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying wx.grid.Grid control.

        """
        style = wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE
        self.widget = wx.grid.Grid(parent, style=style)

    def initialize(self):
        """ Intialize the widget with the attributes of this instance.

        """
        super(WXTableView, self).initialize()
        self.set_table_model(self.shell_obj.item_model)
        self.widget.SetDoubleBuffered(True)

    def bind(self):
        """ Bind the event handlers for the table view.

        """
        super(WXTableView, self).bind()
        widget = self.widget
        widget.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_select_cell)
        widget.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_left_dclick)

    #---------------------------------------------------------------------------
    # implementation
    #---------------------------------------------------------------------------
    def shell_item_model_changed(self, item_model):
        """ The change handler for the 'item_model' attribute.

        """
        self.set_table_model(item_model)

    def shell_vertical_header_visible_changed(self, visible):
        """ The change handler for the 'vertical_header_visible' 
        attribute of the shell object.

        """
        pass

    def shell_horizontal_header_visible_changed(self, visible):
        """ The change handler for the 'horizontal_header_visible'
        attribute of the shell object.

        """
        pass
        
    def on_select_cell(self, event):
        """ The event handler for the cell selection event.  Not meant
        for public consumption.

        """
        event.Skip()

    def on_left_dclick(self, event):
        """ The event handler for the double-click event.  Not meant
        for public consumption.

        """
        event.Skip()

    def set_table_model(self, model):
        """ Set the table view's model.  Not meant for public
        consumption.

        """
        model_wrapper = AbstractItemModelTable(model)
        self.widget.SetTable(model_wrapper)
        self.widget.Refresh()
        self.model_wrapper = model_wrapper

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def size_hint(self):
        """ A reimplemented parent class method which computes the size 
        hint for the table view.

        """
        # This size hint is taken from QAbstractScrollArea::sizeHint
        # which is the size hint implementation for QTableView.
        # The wx GetBestSize() call returns the size for the entire
        # table, which may be millions of pixels for large tables.
        # It also takes forever and a year to compute.
        return (256, 192)
        
