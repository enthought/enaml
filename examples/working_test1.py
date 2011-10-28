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
from enaml.styling.color import Color
from enaml.item_models.abstract_item_model import AbstractTableModel
from enaml.enums import DataRole

with enaml.imports():
    from working_test1 import TestView



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

    @cached_property
    def _get_html_source(self):
        import cgi
        txt = open('./working_test1.enaml').read()
        return '<pre>' + cgi.escape(txt) + '</pre>'

    def pdb(self, obj):
        import pdb; pdb.set_trace()

    def randomize_error_colors(*args):
        pass

class TableModel(AbstractTableModel):

    def column_count(self, parent=None):
        return 1500000

    def row_count(self, parent=None):
        return 5000000

    def data(self, index, role):
        if role == DataRole.DISPLAY:
            return index.row + index.column


if __name__ == '__main__':
    view = TestView()
    view.show()
    print view.ns.nested

