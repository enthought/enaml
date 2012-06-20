#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Instance, Range, on_trait_change, Str

from async_messenger import AsyncMessenger


# NOTE!!!!
#
# This is currently hacked together just to validate the ideas of the
# async message passing, this is certainly not production quality code.

class CommandWidget(AsyncMessenger, HasTraits):

    parent = Instance('CommandWidget')

    def __init__(self, parent=None, **kwargs):
        super(CommandWidget, self).__init__(parent=parent, **kwargs)


class Slider(CommandWidget):

    value = Range(0, 100)

    def receive_update_value(self, ctxt):
        self.value = ctxt['value']


class Label(CommandWidget):
    
    label = Str('Label')

    @on_trait_change('label')
    def update_label(self, label):
        self.send('set_label', dict(label=label))



class Container(CommandWidget):
    
    def show(self):
        self.send('show', {})



from qt_local_application import QtLocalApplication

app = QtLocalApplication()

view = Container()
slider = Slider(view)
label = Label(view)
 
view.children = [slider, label]
slider.children = []
label.children = []

def updater():
    label.label = str(slider.value)

slider.on_trait_change(updater, 'value')

app.create_client_tree(view)

view.show()

app.run()





