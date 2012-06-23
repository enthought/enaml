#------------------------------------------------------------------------------
#  Copyright (c) 2011-2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import types

from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler


class EnamlTestCase(object):
    """ Base class for testing Enaml object widgets.

    This class provide utility methods functions to help the testing of
    enaml components.

    """

    def find_client_widget(self, root, type_name):
        """ A simple function that recursively walks a widget tree until it
        finds a widget of a particular type.

        """
        if root.widget_type == type_name:
            return root

        for child in root.children:
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
        view = ns['MainView']
        return view(**kwargs)

