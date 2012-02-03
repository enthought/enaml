#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase, required_method


class TestSpinBox(EnamlTestCase):
    """ Logic for testing spin boxes.

    Tooklit testcases need to provide the following methods

    Abstract Methods
    ----------------
    def get_value(self, widget)
        Get a spin box's value.

    def get_low(self, widget)
        Get a spin box's minimum value.

    get_high(self, widget)
        Get a spin box's maximum value.

    get_step(self, widget)
        Get a spin box's step size.

    get_wrap(self, widget)
        Check if a spin box wraps around at the edge values.

    get_text(self, widget)
        Get the text displayed in a spin box.

    spin_up_event(self, widget)
        Simulate a click on the 'up' spin button.

    spin_down_event(self, widget)
        Simulate a click on the 'down' spin button.

    """
    def setUp(self):
        """ Set up before the spin box tests.

        """

        enaml_source = """
from enaml.converters import IntConverter
enamldef MainView(MainWindow):
    attr events
    SpinBox:
        name = 'spinbox'
        low = -10
        high = 21
        step = 2
        value = -4
        wrap = True
"""

        self.events = []
        self.view = self.parse_and_create(enaml_source, events=self.events)
        self.component = self.component_by_name(self.view, 'spinbox')
        self.widget = self.component.toolkit_widget

    def test_initial_attributes(self):
        """ Compare the Enaml SpinBox's attributes with its toolkit widget.

        """
        component = self.component
        widget = self.widget

        self.assertEqual(self.get_value(widget), component.value)
        self.assertEqual(self.get_low(widget), component.low)
        self.assertEqual(self.get_high(widget), component.high)
        self.assertEqual(self.get_step(widget), component.step)
        self.assertEqual(self.get_wrap(widget), component.wrap)

    def test_change_low(self):
        """ Update the spin box's minimum value.

        """
        component = self.component
        new_low = component.low - 1
        component.low = new_low
        component_low = component.low
        widget_low = self.get_low(self.widget)

        self.assertEqual(component_low, new_low)
        self.assertEqual(widget_low, component_low)

    def test_change_high(self):
        """ Update the spin box's maximum value.

        """
        component = self.component
        new_high = component.high + 1
        component.high = new_high
        component_high = component.high
        widget_high = self.get_high(self.widget)

        self.assertEqual(component_high, new_high)
        self.assertEqual(widget_high, component_high)

    def test_step_up(self):
        """ Simulate a press of the spin box's 'up' button.

        """
        component = self.component
        widget = self.widget
        old_widget_value = self.get_value(widget)
        widget_step = self.get_step(widget)

        self.spin_up_event(widget)
        new_widget_value = self.get_value(widget)

        self.assertEqual(new_widget_value, old_widget_value + widget_step)
        self.assertEqual(component.value, new_widget_value)

    def test_step_down(self):
        """ Simulate a press of the spin box's 'down' button.

        """
        component = self.component
        widget = self.widget
        old_widget_value = self.get_value(widget)
        widget_step = self.get_step(widget)

        self.spin_down_event(widget)
        new_widget_value = self.get_value(widget)

        self.assertEqual(new_widget_value, old_widget_value - widget_step)
        self.assertEqual(component.value, new_widget_value)

    def test_wrap_top(self):
        """ Check that a spin box wraps appropriately, from top to bottom.

        """
        widget = self.widget
        component = self.component
        component.value = component.high
        self.spin_up_event(self.widget)
        self.assertEqual(component.value, component.low)
        self.assertEqual(component.value, self.get_value(widget))

    def test_wrap_bottom(self):
        """ Check that a spin box wraps appropriately, from bottom to top.

        """
        widget = self.widget
        component = self.component
        component.value = component.low
        self.spin_down_event(widget)
        self.assertEqual(component.value, component.high)
        self.assertEqual(component.value, self.get_value(widget))

    def test_no_wrap_top(self):
        """ Check that a spin box doesn't wrap from top to bottom.

        """
        widget = self.widget
        component = self.component
        high = component.high
        component.wrap = False
        component.value = high
        self.spin_up_event(widget)
        self.assertEqual(component.value, high)
        self.assertEqual(component.value, self.get_value(widget))

    def test_no_wrap_bottom(self):
        """ Check that a spin box doesn't wrap from bottom to top.

        """
        widget = self.widget
        component = self.component
        low = component.low
        component.wrap = False
        component.value = low
        self.spin_down_event(widget)
        self.assertEqual(component.value, low)
        self.assertEqual(component.value, self.get_value(widget))

    def test_text_display(self):
        """ Check the displayed text.

        """
        self.assertEqual(self.get_text(self.widget), '-4')

    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @required_method
    def get_value(self, widget):
        """ Get a spin box's value.

        """
        pass

    @required_method
    def get_low(self, widget):
        """ Get a spin box's minimum value.

        """
        pass

    @required_method
    def get_high(self, widget):
        """ Get a spin box's maximum value.

        """
        pass

    @required_method
    def get_step(self, widget):
        """ Get a spin box's step size.

        """
        pass

    @required_method
    def get_wrap(self, widget):
        """ Check if a spin box wraps around at the edge values.

        """
        pass

    @required_method
    def get_text(self, widget):
        """ Get the text displayed in a spin box.

        """
        pass

    @required_method
    def spin_up_event(self, widget):
        """ Simulate a click on the 'up' spin button.

        """
        pass

    @required_method
    def spin_down_event(self, widget):
        """ Simulate a click on the 'down' spin button.

        """
        pass

