#------------------------------------------------------------------------------
#  Copyright (c) 2011-2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from contextlib import contextmanager
import itertools
import types
import unittest

from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.stdlib.sessions import simple_session

from enaml.qt.qt_application import QtApplication

class TestingQtApplication(QtApplication):
    """ Custom application used only by the testing framework for QT.

    It prevent the application from starting the event loop and exposes a
    function as a context manager to execute a set of actions before forcing the
    events to be processed.

    """
    def start(self):
        """ Start the application's main event loop.

        """
        pass

    @contextmanager
    def process_events(self):
        """ Process all the pending events on the QT event loop.

        This method is for testing only. It runs the event loop and process all
        the events.

        """
        yield

        # From QT Documentation
        # Immediately dispatches all events which have been previously queued
        # with QCoreApplication::postEvent().
        # Events from the window system are not dispatched by this function,
        # but by processEvents().
        self._qapp.sendPostedEvents()

        # Processes all pending events for the calling thread
        self._qapp.processEvents()


_session_counter = itertools.count()
def get_unique_session_identifier():
    """ Returns a 'unique' name for a session. """
    return 'session_%d' % _session_counter.next()


class EnamlTestCase(unittest.TestCase):
    """ Base class for testing Enaml object widgets.

    This class provide utility methods functions to help the testing of
    enaml components.

    """
    def find_client_widget(self, root, type_name):
        """ A simple function that recursively walks a widget tree until it
        finds a widget of a particular type.

        """

        if type_name in [ cls.__name__ for cls in type(root).__mro__]:
            return root.widget()

        for child in root.children():
            found = self.find_client_widget(child, type_name)
            if found is not None:
                return found

        return None

    def find_server_widget(self, root, type_name):
        """ A simple function that recursively walks a widget tree until it
        finds a widget of a particular type.

        """
        if type_name in [cls.__name__ for cls in type(root).__mro__]:
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

        self.app = TestingQtApplication.instance()

        if self.app is None:
            self.app = TestingQtApplication([])

        self.app.add_factories([view_factory])

        session_id = self.app.start_session(session_name)

        self.app.start()

        session = self.app._sessions[session_id]

        # retrieve the enaml server side root widget
        self.view = session.windows[0]

        # retrieve the enaml client side root widget
        self.client_view = self.app._qt_sessions[session_id]._windows[0]

    def tearDown(self):

        self.app.stop()

