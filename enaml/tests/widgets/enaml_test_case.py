#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest
from cStringIO import StringIO

from enaml.factory import EnamlFactory
from enaml.toolkit import default_toolkit

def required_method(function_object):
    """ Decorator for required methods.

    The decorator wraps an *empty* method to raise an NotImplementedError
    with an appropriate error message.

    """
    def proxy_function(self, *args, **kwargs):
        function_name = function_object.__name__
        msg = ("Method '{0}(self, widget, *args, **kwards)' needs to be "
               "implemented for the '{1}' test case".format(function_name, self))
        raise NotImplementedError(msg)
    return proxy_function

def required_extended_method(function_object):
    """ Decorator for required methods that need to have an exteneded signature.

    The decorator wraps an *empty* method to raise an NotImplementedError
    with an appropriate error message.

    """
    def proxy_function(self, *args, **kwargs):
        function_name = function_object.__name__
        msg = ("Method '{0}(self, component, widget, *args, **kwards)' needs to be "
               "implemented for the '{1}' test case".format(function_name, self))
        raise NotImplementedError(msg)
    return proxy_function

class EnamlTestCase(unittest.TestCase):
    """ Base class for testing Enaml object widgets.

    This class provide utility methods and assertion functions to help
    the testing of enaml components

    """

    #: default toolkit to use for the enaml source parsing
    toolkit = default_toolkit()

    def component_by_id(self, view, component_id):
        """ Find an item in the view's namespace with a given id.

        Arguments
        ---------
        view :
            The enaml based view object

        component_id :
            The enaml component id.

        Raises
        ------
        AttributeError :
            if there is no object with that id.

        """
        return getattr(view.ns, component_id)

    def parse_and_create(self, enaml_source, **kwargs):
        """ Parse the test enaml source and returns the enaml view object.

        Arguments
        ---------
        enaml_source : str
            The enaml source to use

        kwargs :
            The models to pass and associate with the view.

        The method parses the enaml_source and creates the enaml view object
        using the desired toolkit and model

        """
        fact = EnamlFactory(StringIO(enaml_source), toolkit=self.toolkit)
        view = fact(**kwargs)

        # Lay widgets out, but don't display them to screen.
        view._apply_style_sheet()
        view.window.layout()

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
        widget = component.toolkit_widget()
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
        widget = component.toolkit_widget()
        enaml_value = getattr(component, attribute_name)
        widget_value = getattr(self, 'get_' + attribute_name)(component, widget)

        self.assertEqual(value, enaml_value)
        self.assertEqual(value, widget_value)
