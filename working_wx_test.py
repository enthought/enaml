""" A working example that tracks the development of the widgets
on the wx branch and can be executed via python working_wx_test.py 
from the current directory.

"""
from cStringIO import StringIO
import random

import wx

from traits.api import HasTraits, Str

from enaml.factory import EnamlFactory

enml = """
import math
import random
import datetime

from enaml.enums import Direction


Window:

    title << model.window_title
    
    Panel:
        HGroup:
            Group my_group:

                direction << (random.choice([Direction.TOP_TO_BOTTOM, 
                                             Direction.BOTTOM_TO_TOP]) 
                              or pb2.clicked)
            
                PushButton:
                    text << "clickme!" if not self.down else "I'm down!"

                    # msg is passed implicitly to any >> notify expressions
                    clicked >> print('clicked!', msg.new)

                PushButton pb2:
                    text = "shuffle"
                    clicked >> setattr(rb1, 'checked', True)

                PushButton static:
                    text = "static"
                    clicked >> model.print_msg(msg)
                
                CheckBox cb1:
                    text = "A simple text box"
                    toggled >> setattr(self, 'text', model.randomize(self.text))
                
            Html:
                source << ("<center><h1>Hello Enaml!</h1></center><br>" * cmbx.value 
                           if not static.down else 
                           "<center><h1>Static Down!</h1></center>")

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
                    activated >> print('activated', msg.new)
                    selected >> print('selected', msg.new)
                    date >> print('new date', msg.new)
                
                ComboBox cmbx:
                    items = range(100)
                    value = 1
                    selected >> print('selected', msg.new)

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
                        toggled >> setattr(cmbx, 'value', 42)
                    SpinBox sb:
                        prefix << 'Foo ' if wrap_box.checked else 'Bar '
                        suffix << ' lb' if wrap_box.checked else ' kg'
                        wrap := wrap_box.checked
                        special_value_text = "Auto"
                        step = 2
                        low << -20 if not self.wrap else 0
                        high = 20
                        #value >> print(self.value)

                HGroup:
                    LineEdit line_edit:
                        text := model.window_title
                Slider:
                    value = 10
                    value >> print(self.value)
                    to_slider = lambda val: math.log10(val)
                    from_slider = lambda val: 10 ** val
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

view = fact(model=Model())

view.show()


