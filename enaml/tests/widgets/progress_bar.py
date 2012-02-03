#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import TraitError

from .enaml_test_case import EnamlTestCase, required_method


class TestProgressBar(EnamlTestCase):
    """ Logic for testing the ProgressBar.

    Tooklit testcases need to provide the following functions

    Abstract Methods
    ----------------
    get_value(self, widget)
        Get the toolkits widget's active value.

    get_minimum(self, widget)
        Get the toolkits widget's minimum value.

    get_maximum(self, widget)
        Get the toolkits widget's maximum value.

    """

    def setUp(self):
        """ Set up before the ProgressBar tests.

        """

        enaml = """
enamldef MainView(MainWindow):
    ProgressBar:
        name = 'test'
"""

        self.view = self.parse_and_create(enaml)
        self.component = self.component_by_name(self.view, 'test')
        self.widget = self.component.toolkit_widget

    def test_initialization_values(self):
        """ Test the initial attributes of the ProgressBar component.

        """
        component = self.component

        self.assertEnamlInSync(component, 'value', 0)
        self.assertEnamlInSync(component, 'minimum', 0)
        self.assertEnamlInSync(component, 'maximum', 100)

    def test_change_minimum(self):
        """ Test changing the minimum value.

        """
        component = self.component
        new_minimum = 10
        component.minimum = new_minimum
        self.assertEnamlInSync(component, 'minimum', new_minimum)

    def test_change_maximum(self):
        """ Test changing the maximum value.

        """
        component = self.component
        new_maximum = 90
        component.maximum = new_maximum
        self.assertEnamlInSync(component, 'maximum', new_maximum)

    def test_change_value_in_enaml(self):
        """ Test changing the current value through the component.

        """
        component = self.component
        new_value = 10
        component.value = new_value
        self.assertEnamlInSync(component, 'value', new_value)

    def test_invalid_minimum(self):
        """ Test changing to an invalid value below the minimum.

        """
        component = self.component
        with self.assertRaises(TraitError):
            component.value = -10
        self.assertEnamlInSync(component, 'value', 0)

    def test_invalid_maximum(self):
        """ Test changing to an invalid value above the maximum.

        """
        component = self.component
        with self.assertRaises(TraitError):
            component.value = 110
        self.assertEnamlInSync(component, 'value', 0)

    def test_change_maximum_and_value(self):
        """ Test setting maximum while the value is out of range.

        """
        component = self.component
        component.value = 90
        component.maximum = 80
        self.assertEnamlInSync(component, 'value', 80)

    def test_change_minimum_and_value(self):
        """ Test setting minimum while the value is out of range.

        """
        component = self.component
        component.minimum = 10
        self.assertEnamlInSync(component, 'value', 10)

    def test_change_range_invalid(self):
        """ Test setting minimum > maximum.

        """
        component = self.component
        with self.assertRaises(TraitError):
            component.maximum = -10

        with self.assertRaises(TraitError):
            component.minimum = 110

    #--------------------------------------------------------------------------
    # Special initialization tests
    #--------------------------------------------------------------------------
    def test_initial_too_large(self):
        """ Check initialization with a value too large for the specified
        maximum.

        """
        enaml = """
enamldef MainView(MainWindow):
    ProgressBar:
        name = 'test'
        value = 95
        minimum = 10
        maximum = 90
"""
        # FIXME: need make a more refined check, this is not the best way
        with self.assertRaises(TraitError):
            self.parse_and_create(enaml)

    def test_initial_too_small(self):
        """ Check initialization with a value too small for the specified
        minimum.

        """

        enaml = """
enamldef MainView(MainWindow):
    ProgressBar:
        name = 'test'
        value = 5
        minimum = 10
        maximum = 90
"""

        # FIXME: need make a more refined check, this is not the best way
        with self.assertRaises(TraitError):
            self.parse_and_create(enaml)

    def test_percentage(self):
        """ Test that the percentage is computed accurately.

        """
        self.component.maximum = 1000
        self.component.value = 999
        # Note the rounding down to 99%.
        self.assertEquals(self.component.percentage, 99)
        self.component.value = 1000
        self.assertEquals(self.component.percentage, 100)
        self.component.value = 899
        # Note the rounding to the nearest integer.
        self.assertEquals(self.component.percentage, 90)
        self.component.value = 0
        self.component.maximum = 0
        self.assertEquals(self.component.percentage, 0)
        self.component.minimum = -1000
        self.assertEquals(self.component.percentage, 100)
        self.component.value = -1
        self.assertEquals(self.component.percentage, 99)

    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @required_method
    def get_value(self, widget):
        """  Get the toolkits widget's active value.

        """
        pass

    @required_method
    def get_minimum(self, widget):
        """  Get the toolkits widget's maximum value attribute.

        """
        pass

    @required_method
    def get_maximum(self, widget):
        """ Get the toolkits widget's minimum value attribute.

        """
        pass

