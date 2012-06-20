#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Instance, Range, on_trait_change, Str, List

from async_messenger import AsyncMessenger


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

    def init_info(self):
        """ Returns an initialization dict.

        """
        info = {}
        info['widget'] = type(self).__name__
        info['msg_id'] = self.msg_id
        info['attrs'] = self.init_attrs()
        child_info = []
        for child in self.children:
            child_info.append(child.init_info())
        info['children'] = child_info
        return info

    def init_attrs(self):
        """ Return a dictionary of initialization attributes.

        """
        return dict()


class Slider(CommandWidget):

    value = Range(0, 100, value=30)

    def init_attrs(self):
        return dict(value=self.value)

    def receive_update_value(self, ctxt):
        self.value = ctxt['value']


class Label(CommandWidget):
    
    label = Str('Label')

    def init_attrs(self):
        return dict(label=self.label)

    @on_trait_change('label')
    def update_label(self, label):
        self.send('set_label', dict(label=label))


class Container(CommandWidget):
        
    def show(self):
        self.send('show', {})


from qt_local_application import QtLocalApplication

app = QtLocalApplication()

view = Container()
slider = Slider()
label = Label()
 
view.add_child(slider)
view.add_child(label)


def updater():
    label.label = str(slider.value)

slider.on_trait_change(updater, 'value')

app.create_clients(view.init_info())

app.run()



