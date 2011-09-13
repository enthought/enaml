""" A working example that tracks the development of the widgets
on the wx branch and can be executed via python working_wx_test.py 
from the current directory.

"""
import random

from traits.api import HasTraits, Str

from enaml.factory import EnamlFactory
from enaml.color import Color
from enaml.util.style_sheet import style


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


fact = EnamlFactory('./working_wx_test.enaml')

view = fact(model=Model())

view.show()

