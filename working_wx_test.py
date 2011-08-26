""" A working example that tracks the development of the widgets
on the wx branch and can be executed via python working_wx_test.py 
from the current directory.

"""
from cStringIO import StringIO
import random

import wx

from traits.api import HasTraits, Str

from traitsml.view_factories.tml import TMLViewFactory

tml = """
from traitsml.enums import Direction
import random

Window:

    Group my_group:

        direction << random.choice(list(Direction.values())) or pb2.clicked

        PushButton:
            text << "clickme!" if not self.down else "I'm down!"

            # args is passed implicitly to any >> notify expressions
            clicked >> print('clicked!', args.new)

        PushButton pb2:
            text = "shuffle"

        PushButton:
            text = "static"
            clicked >> model.print_msg(args)
        
        CheckBox:
            text = "A simple text box"
            toggled >> setattr(self, 'text', model.randomize(self.text))

"""

class Model(HasTraits):
    message = Str('Foo Model Message!')

    def print_msg(self, args):
        print self.message, args

    def randomize(self, string):
        l = list(string)
        random.shuffle(l)
        return ''.join(l)


fact = TMLViewFactory(StringIO(tml))

app = wx.PySimpleApp()

view = fact(model=Model())

view.show()

app.MainLoop()

