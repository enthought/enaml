#------------------------------------------------------------------------------
#  Copyright (c) 2011-2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import itertools
import types
import unittest

from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.stdlib.sessions import simple_session

from .mock_application import MockApplication


_session_counter = itertools.count()
def get_unique_session_identifier():
    """ Returns a 'unique' name for a session. """
    return 'session_{}'.format(_session_counter.next())

class EnamlTestCase(unittest.TestCase):
    """ Base class for testing Enaml object widgets.

    This class provide utility methods functions to help the testing of
    enaml components.

    """


    def find_client_widget(self, root, type_name):
        """ A simple function that recursively walks a widget tree until it
        finds a widget of a particular type.

        """

        if type_name == root.widget_type():
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
        session_name =  get_unique_session_identifier()
        view_factory = simple_session(session_name, 'test', View)

        self.app = MockApplication.instance()

        if self.app is None:
            self.app = MockApplication([])

        self.app.add_factories([view_factory])

        session_id = self.app.start_session(session_name)

        self.app.start()

        session = self.app._sessions[session_id]

        # retrieve the enaml server side root widget
        self.view = session.session_objects[0]

        # retrieve the enaml client side root widget
        self.client_view = self.app._objects[session_id][0]


    def tearDown(self):

        self.app.stop()

