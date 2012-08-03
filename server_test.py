from traits.api import HasTraits, Str, Property, Int, cached_property
import copy
import enaml
from enaml.application import Application
from enaml.session import Session
#from enaml.wx.wx_local_server import WxLocalServer
from enaml.qt.qt_local_server import QtLocalServer
from enaml.stdlib.sessions import view_factory


class Model(HasTraits):
    
    templ = Str('<h1><center>The number is %d</center></h1>')

    value = Int(50)

    html = Property(Str, depends_on=['templ', 'value'])

    @cached_property
    def _get_html(self):
        return self.templ % self.value


class SampleView(Session):
    
    def init(self, model, share_model):
        if not share_model:
            model = copy.copy(model)
        self.model = model

    def on_open(self):
        with enaml.imports():
            from server_test_view import Main
        return [Main(model=self.model)]


@view_factory('foo-view')
def create_view(model):
    with enaml.imports():
        from server_test_view import Main
    return Main(model=model)


if __name__ == '__main__':
    app_model = Model(text='Foo')

    shared_factory = SampleView.factory(
        'test-view-shared',
        "A simple test view which shares the model",
        model=app_model,
        share_model=True,
    )

    unshared_factory = SampleView.factory(
        'test-view-unshared',
        "A simple test view which doesn't share the model",
        model=app_model,
        share_model=False,
    )

    app = Application([shared_factory, unshared_factory, create_view(app_model)])

    #server = WxLocalServer(app)
    server = QtLocalServer(app)

    client = server.local_client()

    # Bring up three ui's, to show how we can link the views with a 
    # common model or not
    client.start_session('test-view-shared')
    client.start_session('test-view-shared')
    client.start_session('test-view-unshared')
    client.start_session('foo-view')
    
    server.start()

