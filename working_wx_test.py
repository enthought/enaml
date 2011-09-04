""" A working example that tracks the development of the widgets
on the wx branch and can be executed via python working_wx_test.py 
from the current directory.

"""
from cStringIO import StringIO
import random

import wx

from traits.api import HasTraits, Str

from enaml.factories.enaml_factory import EnamlFactory

enml = """
import random
import datetime

from enaml.enums import Direction


Window:
    title << model.window_title
    Panel:
        VGroup:
            HGroup:
                PushButton this_button:
                    text = "One"
                PushButton:
                    text = "Two"
                    clicked >> setattr(model, 'window_title', model.randomize(model.window_title))
                PushButton:
                    text = "Three"
            HGroup:
                PushButton:
                    text = "One"
                PushButton:
                    text = "Two"
                PushButton:
                    text = "Three"
            HGroup:
                PushButton:
                    text << "One" if this_button.down else "Four"
                PushButton:
                    text = "Two"
                PushButton:
                    text = "Three"
"""

class Model(HasTraits):

    message = Str('Foo Model Message!')

    window_title = Str('Window Title!')

    def print_msg(self, args):
        print self.message, args

    def randomize(self, string):
        l = list(string)
        random.shuffle(l)
        return ''.join(l)


fact = EnamlFactory(StringIO(enml))

app = wx.PySimpleApp()

view = fact(model=Model())
view.show()

app.MainLoop()

