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
import datetime

Window:
    HGroup:
        Group my_group:

            direction << random.choice(list(Direction.values())) or pb2.clicked
        
            PushButton:
                text << "clickme!" if not self.down else "I'm down!"

                # args is passed implicitly to any >> notify expressions
                clicked >> print('clicked!', args.new)

            PushButton pb2:
                text = "shuffle"
                clicked >> setattr(rb1, 'checked', True)
            PushButton static:
                text = "static"
                clicked >> model.print_msg(args)
            
            CheckBox cb1:
                text = "A simple text box"
                toggled >> setattr(self, 'text', model.randomize(self.text))
            
            RadioButton:
                text = 'foo'
        Html:
            source << "<h1>Hello Html!</h1>" if not static.down else "<h1>Static Down!</h1>"

        VGroup:
            Panel:
                HGroup:
                    direction = Direction.RIGHT_TO_LEFT
                    RadioButton rb1:
                        text = 'rb1'
                        toggled >> print('rb1:', self.checked)
                    RadioButton:
                        text = 'rb2'
                        toggled >> print('rb2:', self.checked)
                    RadioButton:
                        text = 'rb3'
                        toggled >> print('rb3:', self.checked)
                    RadioButton:
                        text = 'rb4'
                        toggled >> print('rb4:', self.checked)
            Panel:
                HGroup:
                    RadioButton:
                        text = 'rb1'
                    RadioButton:
                        text = 'rb2'
                    RadioButton:
                        text = 'rb3'
                    RadioButton:
                        text = 'rb4'
            Calendar:
                minimum_date = datetime.date(1970, 1, 1)
                activated >> print('activated', args.new)
                selected >> print('selected', args.new)
                date >> print('new date', args.new)
            
            HGroup:
                Label:
                    text = 'min:'
                Label:
                    text << str(sb.low)
                Label:
                    text = 'max:'
                Label:
                    text << str(sb.high)
                Label:
                    text = 'val:'
                Label:
                    text << str(sb.value)
            HGroup:
                CheckBox wrap_box:
                    text = 'Allow wrap:'
                SpinBox sb:
                    prefix = 'Foo '
                    suffix = ' kg'
                    wrap := wrap_box.checked
                    special_value_text = "Auto"
                    step = 2
                    low << -20 if not self.wrap else 0
                    high = 20
                    value >> print(self.value)

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

