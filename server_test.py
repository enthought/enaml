from traits.api import HasTraits, Str

import enaml
from enaml.application import Application
from enaml.session import Session
from enaml.zmq_server import ZMQServer


class Model(HasTraits):

    text = Str


class SampleView(Session):

    def on_open(self, model):
        #print 'on open'
        with enaml.imports():
            from server_test_view import Main
        return Main()

    #def on_close(self):
    #    print 'on close'


if __name__ == '__main__':
    app_model = Model(text='Foo')

    app = Application([
        ('test-view', 'A simple test view', SampleView, dict(model=app_model))
    ])

    server = ZMQServer(app, '127.0.0.1', '8888')

    server.start()

