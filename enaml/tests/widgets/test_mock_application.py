import types
import unittest

from enaml.application import Application
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.core.parser import parse
from enaml.stdlib.sessions import simple_session

from enaml.tests.widgets.mock_request import MockLocalServer


class MockApplicationTestCase(unittest.TestCase):

    def test_creation(self):

        source = """
from enaml.widgets.api import MainWindow

enamldef MainView(MainWindow):
    title = 'test'
"""
        enaml_ast = parse(source)
        enaml_module = types.ModuleType('__tests__')
        ns = enaml_module.__dict__
        code = EnamlCompiler.compile(enaml_ast, '__enaml_tests__')

        exec code in ns
        View = ns['MainView']

        v = simple_session('main', 'test', View)

        app = Application([v])

        server = MockLocalServer(app)

        client = server.local_client()

        client.start_session('main')

        server.start()


if __name__ == '__main__':
    unittest.main()
