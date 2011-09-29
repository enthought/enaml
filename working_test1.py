#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A working example that tracks the development of the widgets
on the wx branch and can be executed via python working_wx_test.py 
from the current directory.

"""
import random

from traits.api import HasTraits, Str, Property, cached_property

import enaml
from enaml.color import Color
from enaml.style_sheet import style
from enaml.item_models.abstract_item_model import AbstractTableModel
from enaml.enums import DataRole

with enaml.imports():
    from working_test1 import MainWindow


colors = Color.color_map.keys()


class Model(HasTraits):

    message = Str('Foo Model Message!')

    window_title = Str('Window Title!')

    html_source = Property(Str)

    def print_msg(self, args):
        print self.message, args

    def randomize(self, string):
        l = list(string)
        random.shuffle(l)
        return ''.join(l)

    def randomize_error_colors(self):
        sty = style('.error_colors', 
            color = random.choice(colors),
            background_color=random.choice(colors),
        )
        view.style_sheet.update(sty)

    @cached_property
    def _get_html_source(self):
        import cgi
        txt = open('./working_test1.enaml').read() 
        return '<pre>' + cgi.escape(txt) + '</pre>'


class TableModel(AbstractTableModel):
        
    def column_count(self, parent=None):
        return 1500000
    
    def row_count(self, parent=None):
        return 5000000

    def data(self, index, role):
        if role == DataRole.DISPLAY:
            return index.row + index.column


view = MainWindow(model=Model(), table_model=TableModel())

view.show()

