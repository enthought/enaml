""" A working example that tracks the development of the widgets
on the wx branch and can be executed via python working_wx_test.py 
from the current directory.

"""
import random

from traits.api import HasTraits, Str

from enaml.factory import EnamlFactory
from enaml.color import Color
from enaml.style_sheet import style
from enaml.item_models.abstract_item_model import AbstractTableModel
from enaml.enums import DataRole


colors = Color.color_map.keys()


class Model(HasTraits):

    message = Str('Foo Model Message!')

    window_title = Str('Window Title!')

    def print_msg(self, args):
        print self.message, args

    def randomize(self, string):
        l = list(string)
        random.shuffle(l)
        return ''.join(l)

    def update_style(self):
        sty = style('.error_colors', 
            color = random.choice(colors),
            background_color=random.choice(colors),
        )
        view.style_sheet.update(sty)


class TableModel(AbstractTableModel):
        
    def column_count(self, parent=None):
        return 1500000
    
    def row_count(self, parent=None):
        return 5000000

    def data(self, index, role):
        if role == DataRole.DISPLAY:
            return index.row + index.column


fact = EnamlFactory('./working_test1.enaml')

view = fact(model=Model(), table_model=TableModel())

view.show()

