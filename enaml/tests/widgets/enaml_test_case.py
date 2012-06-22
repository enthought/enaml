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

