#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from PySide.QtGui import QSlider, QLabel, QWidget, QPushButton

from async_application import AsyncApplication


# NOTE!!!!
#
# This is currently hacked together just to validate the ideas of the
# async message passing, this is certainly not production quality code.


class ClientWidget(object):

    def __init__(self, msg_id):
        self.__msg_id = msg_id
        self.widget = None
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def send(self, msg, ctxt):
        app = AsyncApplication.instance()
        if app is None:
            return
        app.recv_message(self.__msg_id, msg, ctxt)

    def recv(self, msg, ctxt):
        handler_name = 'receive_' + msg
        handler = getattr(self, handler_name, None)
        if handler is not None:
            return handler(ctxt)
        return NotImplemented

    def create(self, parent, init_attrs):
        raise NotImplementedError


class QtSlider(ClientWidget):

    def create(self, parent, init_attrs):
        self.widget = QSlider(parent)
        self.widget.valueChanged.connect(self.on_value_changed)
        self.widget.show()
        self.widget.move(init_attrs['x'], init_attrs['y'])
        self.widget.setValue(init_attrs.get('value', 0))

    def on_value_changed(self):
        self.send('update_value', dict(value=self.widget.value()))

    def receive_set_value(self, ctxt):
        self.widget.setValue(ctxt['value'])


class QtLabel(ClientWidget):

    def create(self, parent, init_attrs):
        self.widget = QLabel(parent)
        self.widget.show()
        self.widget.move(20, 20)
        self.widget.resize(50, 20)
        self.widget.setText(init_attrs.get('label', ''))

    def receive_set_label(self, ctxt):
        self.widget.setText(ctxt['label'])


class QtContainer(ClientWidget):

    def create(self, parent, attrs):
        self.widget = QWidget(parent)
        self.widget.show()

    def receive_show(self, ctxt):
        self.widget.show()


class QtPushButton(ClientWidget):

    def create(self, parent, attrs):
        self.widget = QPushButton(parent)
        self.widget.setText(attrs['text'])
        self.widget.move(attrs['x'], attrs['y'])
        self.widget.clicked.connect(self.on_clicked)
        self.widget.show()

    def on_clicked(self):
        self.send('clicked', {})


CLIENTS = {
    'Slider': QtSlider,
    'Label': QtLabel,
    'Container': QtContainer,
    'PushButton': QtPushButton,
}


