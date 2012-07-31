from traits.api import HasTraits, Str, Property, Int, cached_property
import copy
import enaml
from enaml.application import Application
from enaml.session import Session
from enaml.qt.qt_local_server import QtLocalServer


class Model(HasTraits):
    
    templ = Str('<h1><center>The number is %d</center></h1>')

    value = Int(50)

    html = Property(Str, depends_on=['templ', 'value'])

    @cached_property
    def _get_html(self):
        return self.templ % self.value


class SampleView(Session):

    def on_open(self, model, share_model):
        with enaml.imports():
            from server_test_view import Main
        if not share_model:
            model = copy.copy(model)
        return Main(model=model)


if __name__ == '__main__':
    app_model = Model(text='Foo')
    kwargs = {
        'model': app_model,
        'share_model': True, # Set this to False to unlink the views
    }

    app = Application([
        ('test-view', 'A simple test view', SampleView, kwargs)
    ])

    server = QtLocalServer(app)

    client = server.local_client()

    # Bring up two ui's, to show how we can link the views with a 
    # common model
    client.start_session('test-view')
    client.start_session('test-view')
    
    server.start()

