#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest
from cStringIO import StringIO

from enaml.factory import EnamlFactory
from enaml.toolkit import default_toolkit

class EnamlTestCase(unittest.TestCase):
    """ Base class for testing Enaml object widgets.

    The following methods are required to be defined by the user in
    order to be able to create an object.

    """

    #: toolkit implementation ot use during testing
    toolkit = default_toolkit()

    def setUp(self):
        """ Parse the test enaml source and get ready for the tests.

        Test subclasses need to set the self.enaml attribute to a valid
        enaml source and (optional) define the toolkit to use through the
        self.toolkit attribute. The enaml source stored in `self.enaml` is
        parsed using the desired toolkit `self.toolkit` and store the
        view.

        This class only provides a basic mechanism for these
        procedures. Additional setUp tasks are ussualy required so derived
        class  need to overdire the method and call the parent setUp
        before they continue with the testcase setup.

        """
        events = []
        fact = EnamlFactory(StringIO(self.enaml), toolkit=self.toolkit)
        view = fact(events=events)

        # Lay widgets out, but don't display them to screen.
        view._apply_style_sheet()
        view.window.layout()

        self.namespace = view.ns
        self.view = view
        self.events = events

    def widget_by_id(self, widget_id):
        """ Find an item in the view's namespace with a given id.

        Raises
        ------
        AttributeError
            if no there is no object with that id.

        """
        return getattr(self.namespace, widget_id)

    def assertEnamlInSync(self, component, attribute_name, value):
        """ Verify that the requested attribute is properly set

        Arguments
        ---------
        component : enaml.widgets.component.Component
            The Enaml component to check
        
        attribute_name : str
            The string name of the Enaml attribute to check.

        value :
            The expected value

        .. note:: It is expected that the user has defined a
            get_<attribute_name>(widget) method in the current test case.
            The get methods can themself raise assertion errors when it
            is not possible to retrieve a sensible value for the attribute.

        """
        widget = component.toolkit_widget()
        enaml_value = getattr(component, attribute_name)
        widget_value = getattr(self, 'get_' + attribute_name)(widget)

        self.assertEqual(value, enaml_value)
        self.assertEqual(value, widget_value)

    def clean_event_queue(self):
        """ Cleans the event queue

        """
        events = self.events
        while len(events):
            events.pop()



