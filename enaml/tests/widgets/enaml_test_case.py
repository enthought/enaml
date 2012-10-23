#------------------------------------------------------------------------------
#  Copyright (c) 2011-2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import types
import unittest

from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.application import Application
from enaml.stdlib.sessions import simple_session

from .mock_server import MockLocalServer


class EnamlTestCase(unittest.TestCase):
    """ Base class for testing Enaml object widgets.

    This class provide utility methods functions to help the testing of
    enaml components.

    """

    def find_client_widget(self, root, type_name):
        """ A simple function that recursively walks a widget tree until it
        finds a widget of a particular type.

        """

        print root.widget()
        if type_name == root.widget()['class']:
            return root

        for child in root.children():
            found = self.find_client_widget(child, type_name)
            if found is not None:
                return found

        return None

    def find_server_widget(self, root, type_name):
        """ A simple function that recursively walks a widget tree until it
        finds a widget of a particular type.

        """
        if root.__class__.__name__ == type_name:
            return root

        for child in root.children:
            found = self.find_server_widget(child, type_name)
            if found is not None:
                return found

        return None

    def parse_and_create(self, source, **kwargs):
        """ Parses and compiles the source. The source should have a
        component defined with the name 'MainView'.

        Arguments
        ---------
        source : str
            The enaml source file

        kwargs : dict
            The default attribute values to pass to the component.

        Returns
        -------
            The component tree for the 'MainView' component.

        """
        enaml_ast = parse(source)
        enaml_module = types.ModuleType('__tests__')
        ns = enaml_module.__dict__
        code = EnamlCompiler.compile(enaml_ast, '__enaml_tests__')

        exec code in ns
        View = ns['MainView']

        # Start the app instance first.
        view_factory = simple_session('main', 'test', View)

        self.app = Application([view_factory])

        server = MockLocalServer(self.app)
        client = server.local_client()

        client.start_session('main')

        self.server = server

        server.start()

        session_id = client._client_sessions.keys()[0]

        server_view_id = self.app._sessions[session_id]._widgets.keys()[0]
        # retrieve the enaml server side root widget
        self.view = self.app._sessions[session_id]._widgets[server_view_id]

        session = client._client_sessions[session_id]
        # retrieve the enaml client side root widget
        self.client_view = session._widgets[session._widgets.keys()[0]]

