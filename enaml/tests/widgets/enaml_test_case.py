#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

from enaml.parsing.parser import parse
from enaml.parsing.enaml_compiler import EnamlCompiler, evalcode
from enaml.widgets.component import Component
from enaml.toolkit import default_toolkit

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

    #: default toolkit to use for the enaml source parsing
    toolkit = default_toolkit()

##    def component_by_id(self, component, component_id):
##        """ Find an item in the view's namespace with a given id.
##
##        Arguments
##        ---------
##        view :
##            The enaml based view object
##
##        component_id :
##            The enaml component id.
##
##        Raises
##        ------
##        AttributeError :
##            if there is no object with that id.
##
##        """
##        return getattr(view.ns, component_id)

    def component_by_name(self, component, name):
        """ Find an item in the view with a given name.

        Arguments
        ---------
        view :
            The enaml based view object

        name :
            The enaml component name.

        Returns
        -------
            The coresponding component or None.

        """
        # FIXME: This is really an ID, not a name, but the tests currently use
        # component_by_name().
        if getattr(component, '__id__', None) == name:
            result = component
        else:
            result = None
            for child in component.children:
                 result = self.component_by_name(child, name)
                 if result is not None:
                    break

        return result

    def parse_and_create(self, source, **kwargs):
        """ parses and compiles the source and returns the enaml view object.

        Arguments
        ---------
        enaml_source : str
            The enaml source file

        kwargs :
            The models to pass and associate with the view.

        The method parses the enaml_source and creates the enaml view object
        using the desired toolkit and model

        """
        enaml_ast = parse(source)
        enaml_module = {}
        EnamlCompiler.compile(enaml_ast, enaml_module)

        toolkit = self.toolkit

        with toolkit:
            defn = enaml_module['MainWindow']
            f_locals = defn._build_locals((), kwargs)
            view = evalcode(defn.__code__, defn.__globals__, f_locals)[0]
            # Assign the computed IDs to the objects.
            # FIXME: This should be done in the VM.
            for enaml_id, obj in f_locals.iteritems():
                if isinstance(obj, Component):
                    obj.__id__ = enaml_id

        self.app = toolkit.create_app()
        view.setup()
        return view


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
            method get_<attribute_name>(widget) in the current test case.
            The get methods can raise assertion errors when it is
            not possible to retrieve a sensible value for the attribute.

        """
        widget = component.toolkit_widget
        enaml_value = getattr(component, attribute_name)
        widget_value = getattr(self, 'get_' + attribute_name)(widget)

        self.assertEqual(value, enaml_value)
        self.assertEqual(value, widget_value)

    def assertEnamlInSyncExtended(self, component, attribute_name, value):
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
            method get_<attribute_name>(component, widget) in the current
            test case. The extended signature is required because additional
            information component attribute are required return a sensible
            result (e.g. the component uses Converters to set and retrieve
            the value of the attribute. The get methods can raise
            assertion errors when it is not possible to retrieve a sensible
            value for the attribute.

        """
        widget = component.toolkit_widget
        enaml_value = getattr(component, attribute_name)
        widget_value = getattr(self, 'get_' + attribute_name)(component, widget)

        self.assertEqual(value, enaml_value)
        self.assertEqual(value, widget_value)
