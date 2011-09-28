#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import abc

from .enaml_test_case import EnamlTestCase
from enaml.enums import TickPosition, Orientation

class TestSlider(EnamlTestCase):
    """ Logic for testing spin boxes.


    Tooklit testcases need to provide the following methods

    Abstract Methods
    ----------------

    """

    __metaclass__  = abc.ABCMeta

    enaml = """
Window:
    Panel:
        VGroup:
            Slider slider:
                tick_interval = 0.1
                value = 0.5
                moved >> events.append('moved')
                pressed >> events.append('pressed')
                released >> events.append('released')
"""

    def setUp(self):
        """ Set up before the spin box tests.

        """
        super(TestSlider, self).setUp()
        component = self.widget_by_id('slider')
        self.widget = component.toolkit_widget()
        self.component = component

    def test_initial_attributes(self):
        """ Compare the Enaml Slider's attributes with its toolkit widget.

        """
        component = self.component

        self.assertFalse(component.error)
        self.assertIsNone(component.exception)

        self.verify_attribute('value', 0.5, component)
        self.verify_attribute('tick_interval', 0.1, component)
        # while the initial value of the tick position is DEFAULT inside the
        # enaml object is converted to BOTTOM
        self.verify_attribute('tick_position', TickPosition.BOTTOM, component)
        self.verify_attribute('orientation', Orientation.HORIZONTAL, component)
        self.verify_attribute('single_step', 1, component)
        self.verify_attribute('page_step', 5, component)


    def test_tracking_attribute(self):
        """ Test accesing tracking attribute

        """
        component = self.component

        self.verify_attribute('tracking', True, component)

        component.tracking = False
        self.verify_attribute('tracking', False, component)


    def testValueChange(self):
        """Test changing the value programmaticaly.

        """
        component = self.component

        component.value = 1
        self.verify_attribute('value', 1, component)
        component.value = 0.879
        self.verify_attribute('value', 0.879, component)

    def testInvalidValueChange(self):
        """ Test changing the position with the an invalid value

        when invalid, check that it has not changed the values and the
        errors are updated.
        """
        component = self.component

        component.value = -0.2
        self.verify_attribute('value', 0.5, component)


        component.value = 3
        self.verify_attribute('value', 0.5, component)

    def testErrorUpdate(self):
        """ Check that errors are assinged

        """
        component = self.component

        component.value = -0.2
        self.assertTrue(component.error)
        self.assertIsInstance(component.exception, ValueError)

        component.value = 3
        self.assertTrue(component.error)
        self.assertIsInstance(component.exception, ValueError)

    def testErrorReset(self):
        """ Check that the error attributes are reset

        """
        component = self.component

        component.value = -0.2
        component.value = 0.3
        self.assertFalse(component.error)
        self.assertIsNone(component.exception)


    def testOrientationSetting(self):
        """ Test changing the widget orientation

        """
        component = self.component

        self.component.orientation = Orientation.VERTICAL
        self.verify_attribute('orientation', Orientation.VERTICAL, component)

        self.component.orientation = Orientation.HORIZONTAL
        self.verify_attribute('orientation', Orientation.HORIZONTAL, component)

    def testTickPositionSetting(self):
        """ Test changing the widget tickposition

        """
        component = self.component

        component.tick_position = TickPosition.BOTTOM
        self.verify_attribute('tick_position', TickPosition.BOTTOM, self.component)

        component.tick_position = TickPosition.TOP
        self.verify_attribute('tick_position', TickPosition.TOP, self.component)

        component.tick_position = TickPosition.BOTH
        self.verify_attribute('tick_position', TickPosition.BOTH, self.component)

        self.component.orientation = Orientation.VERTICAL

        component.tick_position = TickPosition.LEFT
        self.verify_attribute('tick_position', TickPosition.LEFT, self.component)

        component.tick_position = TickPosition.RIGHT
        self.verify_attribute('tick_position', TickPosition.RIGHT, self.component)

        component.tick_position = TickPosition.BOTH
        self.verify_attribute('tick_position', TickPosition.BOTH, self.component)

        component.tick_position = TickPosition.NO_TICKS
        self.verify_attribute('tick_position', TickPosition.NO_TICKS, self.component)

    def testIncompatibleTickPosition(self):
        """ Test that changing tick position is ignored if the orientation
        is not compatible.

        """

        component = self.component

        component.tick_position = TickPosition.BOTTOM
        self.verify_attribute('tick_position', TickPosition.BOTTOM, self.component)

        component.tick_position = TickPosition.LEFT
        self.verify_attribute('tick_position', TickPosition.BOTTOM, self.component)

        component.tick_position = TickPosition.RIGHT
        self.verify_attribute('tick_position', TickPosition.BOTTOM, self.component)

        self.component.orientation = Orientation.VERTICAL

        component.tick_position = TickPosition.BOTTOM
        self.verify_attribute('tick_position', TickPosition.RIGHT, self.component)

        component.tick_position = TickPosition.TOP
        self.verify_attribute('tick_position', TickPosition.RIGHT, self.component)


    def testChangingOrientaionTickPolicy(self):
        """ Test that the ticks follow the orientation changes

        """
        component = self.component

        self.component.orientation = Orientation.VERTICAL
        self.verify_attribute('tick_position', TickPosition.RIGHT, self.component)

    #--------------------------------------------------------------------------
    # absrtact methods
    #--------------------------------------------------------------------------

    @abc.abstractmethod
    def get_value(self, widget):
        """ Get the Slider's value.

        """
        return NotImplemented

    @abc.abstractmethod
    def get_tick_interval(self, widget):
        """ Get the Slider's tick_interval value.

        """
        return NotImplemented

    @abc.abstractmethod
    def get_tick_position(self, widget):
        """ Get the Slider's tick position style.

        """
        return NotImplemented

    @abc.abstractmethod
    def get_orientation(self, widget):
        """ Get the Slider's orientation.

        """
        return NotImplemented

    @abc.abstractmethod
    def get_single_step(self, widget):
        """ Get the Slider's single step value.

        """
        return NotImplemented

    @abc.abstractmethod
    def get_page_step(self, widget):
        """ Get the Slider's page step value.

        """
        return NotImplemented

    @abc.abstractmethod
    def get_tracking(self, widget):
        """ Get the Slider's tracking status.

        """
        return NotImplemented
