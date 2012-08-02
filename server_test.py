from traits.api import HasTraits, Str, Property, Int, cached_property
import copy
import enaml
from enaml.application import Application
from enaml.session import Session
from enaml.wx.wx_local_server import WxLocalServer
#from enaml.qt.qt_local_server import QtLocalServer


class Model(HasTraits):
    
    templ = Str('<h1><center>The number is %d</center></h1>')

    value = Int(50)

    html = Property(Str, depends_on=['templ', 'value'])

    @cached_property
    def _get_html(self):
        return self.templ % self.value


class SampleView(Session):
    
    def initialize(self, model, share_model):
        if not share_model:
            model = copy.copy(model)
        self.model = model

    def on_open(self):
        with enaml.imports():
            from server_test_view import Main
        return Main(model=self.model)


if __name__ == '__main__':
    app_model = Model(text='Foo')
    shared_handler = SampleView.create_handler(
        session_name='test-view-shared',
        session_description="A simple test view which shares the model",
        model=app_model,
        share_model=True,
    )
    unshared_handler = SampleView.create_handler(
        session_name='test-view-unshared',
        session_description="A simple test view which doesn't share the model",
        model=app_model,
        share_model=False,
    )

    app = Application([shared_handler, unshared_handler])

    server = WxLocalServer(app)
    #server = QtLocalServer(app)

    client = server.local_client()

    # Bring up three ui's, to show how we can link the views with a 
    # common model or not
    client.start_session('test-view-shared')
    client.start_session('test-view-shared')
    client.start_session('test-view-unshared')
    
    server.start()

