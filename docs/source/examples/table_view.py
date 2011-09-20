#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory
from enaml.item_models.abstract_item_model import AbstractTableModel
from enaml.enums import DataRole

class TableModel(AbstractTableModel):
    def column_count(self, parent=None):
        return 4

    def row_count(self, parent=None):
        return 3
    
    def data(self, index, role):
        if role == DataRole.DISPLAY:
            return index.row + index.column

enml = """
Window:
    title = "TableView example"
    Panel:
        HGroup:
            TableView:
               item_model = table_model 
"""

fact = EnamlFactory(StringIO(enml))

view = fact(table_model=TableModel())

view.show()
