#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest
import inspect
import types

from enaml import default_toolkit
from enaml.core.parser import parse
from enaml.core.enaml_compiler import EnamlCompiler


def required_method(function_object):
    """ Decorator for required methods.

    The decorator wraps an *empty* method to raise an NotImplementedError
    with an appropriate error message.

    """
    def proxy_function(self, *args, **kwargs):
        function_name = function_object.__name__
        msg = ("Method '{0}' needs to be implemented for the '{1}' test case".\
                format(function_name, self))
        raise NotImplementedError(msg)
    return proxy_function


class EnamlTestCase(unittest.TestCase):
    """ Base class for testing Enaml object widgets.

    This class provide utility methods and assertion functions to help
    the testing of enaml components

    """
    # default toolkit to use for the enaml source parsing
    toolkit = default_toolkit()

    def component_by_name(self, component, name):
        """ Find an item in the view with a given name. The component
        should have the name set its 'name' attribute.

        Arguments
        ---------
        component : BaseComponent
            The enaml based BaseComponent object.

        name : str
            The name of the enaml component to find in the tree.

        Returns
        -------
            The corresponding component or None.

        """
        return component.find_by_name(name)

    def parse_and_create(self, source, **kwargs):
        """ Parses and compiles the source. The source should have a
        component defined with the name 'MainView'. 

        Arguments
        ---------
        source : str
            The enaml source file

        kwargs : dict
            The default attribute values to pass to the component.

        """
        enaml_ast = parse(source)
        enaml_module = types.ModuleType('__tests__')
        ns = enaml_module.__dict__
        code = EnamlCompiler.compile(enaml_ast, '__enaml_tests__')

        toolkit = self.toolkit

        with toolkit:
            exec code in ns
            view = ns['MainView']
            cmpnt = view(**kwargs)

        toolkit.app.initialize()
        self.app = toolkit.app.app_object()
        cmpnt.setup()
        return cmpnt

    def assertEnamlInSync(self, component, attribute_name, value):
        """ Verify that the requested attribute is properly set

        The method compares the attribute value in the Enaml object and
        check if it is synchronized with the toolkit widget. The component
        attribute is retrieved directly while the widget value is retrieved
        through a call to a method function in the test case.

        Arguments
        ---------
        component : enaml.widgets.component.Component
            The Enaml component to check.

        attribute_name : str
            The string name of the Enaml attribute to check.

        value :
            The expected value.

        .. note:: It is expected that the user has defined an appropriate
            method get_<attribute_name>(widget) or the extentded version
            get_<attribute_name>(component, widget) in the current test
            case. The extended signature is commonly used because additional
            information on the component's attributes is required to return
            a sensible result (e.g. the component uses Converters to set
            and retrieve the value of the attribute). The assert method
            The get methods can raise assertion errors when it is not
            possible to retrieve a sensible value for the attribute.

        """
        widget = component.toolkit_widget
        enaml_value = getattr(component, attribute_name)
        widget_method = getattr(self, 'get_' + attribute_name)

        try:
            inspect.getcallargs(widget_method, widget)
        except TypeError:
            widget_value = widget_method(component, widget)
        else:
            widget_value = widget_method(widget)

        self.assertEqual(value, enaml_value)
        self.assertEqual(value, widget_value)

