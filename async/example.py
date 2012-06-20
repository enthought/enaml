#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Instance, Range, on_trait_change, Str, List, Int, Event

from async_messenger import AsyncMessenger
from async_application import AbstractBuilder, AsyncApplication

# NOTE!!!!
#
# This is currently hacked together just to validate the ideas of the
# async message passing, this is certainly not production quality code.

class CommandWidget(AsyncMessenger, HasTraits):

    parent = Instance('CommandWidget')

    children = List(Instance('CommandWidget'))

    def __init__(self, parent=None, **kwargs):
        super(CommandWidget, self).__init__(parent=parent, **kwargs)

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def build_info(self):
        """ Returns an initialization dict.

        """
        info = {}
        info['widget'] = type(self).__name__
        info['msg_id'] = self.msg_id
        info['attrs'] = self.init_attrs()
        child_info = []
        for child in self.children:
            child_info.append(child.build_info())
        info['children'] = child_info
        return info

    def init_attrs(self):
        """ Return a dictionary of initialization attributes.

        """
        return dict()


class Slider(CommandWidget):

    value = Range(0, 100, value=30)

    x = Int
    
    y = Int

    def init_attrs(self):
        return dict(value=self.value, x=self.x, y=self.y)

    def receive_update_value(self, ctxt):
        self.value = ctxt['value']

    @on_trait_change('value')
    def update_value(self, val):
        reply = self.send('set_value', dict(value=val))
        reply.set_failback(self.on_fail)

    def on_fail(self, failure):
        print failure


class Label(CommandWidget):
    
    label = Str('Label')

    def init_attrs(self):
        return dict(label=self.label)

    @on_trait_change('label')
    def update_label(self, label):
        self.send('set_label', dict(label=label))


class PushButton(CommandWidget):

    clicked = Event

    x = Int
    
    y = Int

    text = Str('button')

    def init_attrs(self):
        return dict(text=self.text, x=self.x, y=self.y)

    def receive_clicked(self, ctxt):
        self.clicked = True


class Container(CommandWidget):
    
    _builder = Instance(AbstractBuilder)

    def show(self):
        builder = self._builder
        if builder is None:
            builder = self._builder = AsyncApplication.instance().builder()
            build_info = self.build_info()
            builder.build(build_info)
        self.send('show', {})

    def __del__(self):
        print 'container dying'


from qt_local_application import QtLocalApplication

app = QtLocalApplication()

view = Container()
slider = Slider(x=100, y=100)
label = Label()
slider2 = Slider(x=150, y=150)
button = PushButton(x=50, y=50)

view.add_child(slider)
view.add_child(label)
view.add_child(slider2)
view.add_child(button)

def updater():
    label.label = str(slider.value)
    slider2.value = slider.value

def printer():
    print 'clicked'

slider.on_trait_change(updater, 'value')
button.on_trait_change(printer, 'clicked')

view.show()

app.run()

