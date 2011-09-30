#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import abc

from .enaml_test_case import EnamlTestCase
from enaml.enums import TickPosition, Orientation
from enaml.util.enum import Enum

class TestEvents(Enum):
    """ Events required by the testcase. """

    #: The left button is pressed
    PRESSED = 0x0

    #: The left button is released
    RELEASED = 0x1

    #: The thumb is moved one step up
    STEP_UP = 0x2

    #: The thumb is moved one step down
    STEP_DOWN = 0x3

    #: The thumb is moved one page up
    PAGE_UP = 0x4

    #: The thumb is moved one page down
    PAGE_DOWN = 0x5

    #: The thumb is moved to home
    HOME = 0x6

    #: The thumb is moved to the end
    END = 0x7


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
                page_step = 2
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

        self.assertEnamlInSync(component, 'value', 0.5)
        self.assertEnamlInSync(component, 'tick_interval', 0.1)
        # while the initial value of the tick position is DEFAULT inside the
        # enaml object is converted to BOTTOM
        self.assertEnamlInSync(component, 'tick_position', TickPosition.BOTTOM)
        self.assertEnamlInSync(component, 'orientation', Orientation.HORIZONTAL)
        self.assertEnamlInSync(component, 'single_step', 1)
        self.assertEnamlInSync(component, 'page_step', 2)


    def test_tracking_attribute(self):
        """ Test accesing tracking attribute

        """
        component = self.component

        self.assertEnamlInSync(component, 'tracking', True)

        component.tracking = False
        self.assertEnamlInSync(component, 'tracking', False)


    def testValueChange(self):
        """Test changing the value programmaticaly.

        """
        component = self.component

        component.value = 1
        self.assertEnamlInSync(component, 'value', 1)
        component.value = 0.879
        self.assertEnamlInSync(component, 'value', 0.879)

    def testInvalidValueChange(self):
        """ Test changing the position with the an invalid value

        when invalid, check that it has not changed the values and the
        errors are updated.
        """
        component = self.component

        component.value = -0.2
        self.assertEnamlInSync(component, 'value', 0.5)


        component.value = 3
        self.assertEnamlInSync(component, 'value', 0.5)

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
        self.assertEnamlInSync(component, 'orientation', Orientation.VERTICAL)

        self.component.orientation = Orientation.HORIZONTAL
        self.assertEnamlInSync(component, 'orientation', Orientation.HORIZONTAL)

    def testTickPositionSetting(self):
        """ Test changing the widget tickposition

        """
        component = self.component

        component.tick_position = TickPosition.BOTTOM
        self.assertEnamlInSync(component, 'tick_position', TickPosition.BOTTOM)

        component.tick_position = TickPosition.TOP
        self.assertEnamlInSync(component, 'tick_position', TickPosition.TOP)

        component.tick_position = TickPosition.BOTH
        self.assertEnamlInSync(component, 'tick_position', TickPosition.BOTH)

        self.component.orientation = Orientation.VERTICAL

        component.tick_position = TickPosition.LEFT
        self.assertEnamlInSync(component, 'tick_position', TickPosition.LEFT)

        component.tick_position = TickPosition.RIGHT
        self.assertEnamlInSync(component, 'tick_position', TickPosition.RIGHT)

        component.tick_position = TickPosition.BOTH
        self.assertEnamlInSync(component, 'tick_position', TickPosition.BOTH)

        component.tick_position = TickPosition.NO_TICKS
        self.assertEnamlInSync(component, 'tick_position', TickPosition.NO_TICKS)

    def testIncompatibleTickPosition(self):
        """ Test that changing tick position is ignored if the orientation
        is not compatible.

        """

        component = self.component

        component.tick_position = TickPosition.BOTTOM
        self.assertEnamlInSync(component, 'tick_position', TickPosition.BOTTOM)

        component.tick_position = TickPosition.LEFT
        self.assertEnamlInSync(component, 'tick_position', TickPosition.BOTTOM)

        component.tick_position = TickPosition.RIGHT
        self.assertEnamlInSync(component, 'tick_position', TickPosition.BOTTOM)

        self.component.orientation = Orientation.VERTICAL

        component.tick_position = TickPosition.BOTTOM
        self.assertEnamlInSync(component, 'tick_position', TickPosition.RIGHT)

        component.tick_position = TickPosition.TOP
        self.assertEnamlInSync(component, 'tick_position', TickPosition.RIGHT)


    def testChangingOrientaionTickPolicy(self):
        """ Test that the ticks follow the orientation changes

        """
        component = self.component

        self.component.orientation = Orientation.VERTICAL
        self.assertEnamlInSync(component, 'tick_position', TickPosition.RIGHT)


    def testPressingTheThumb(self):
        """ Test firing events when the thumb is pressed down.

        """
        component = self.component
        events = self.events

        self.sent_event(self.widget, TestEvents.PRESSED)
        self.assertEqual(['pressed'], events)

    def testReleasingTheThumb(self):
        """ Test firing events when the thumb is released.

        """
        self.clean_event_queue()

        component = self.component
        events = self.events

        self.sent_event(self.widget, TestEvents.RELEASED)
        self.assertEqual([], events)

        self.sent_event(self.widget, TestEvents.PRESSED)
        self.sent_event(self.widget, TestEvents.RELEASED)
        self.assertEqual(['pressed', 'released'], events)

    def testMovingTheThumbProgrammaticaly(self):
        """ Test firing events when the thumb is moved (programmatically).

        """
        component = self.component
        events = self.events

        component.value = 0.3
        self.assertEqual(['moved'], events)

    def testMovingToHome(self):
        """ Test firing events and value when the thumb is moved to home.

        """
        component = self.component
        events = self.events

        self.sent_event(self.widget, TestEvents.HOME)
        self.assertEnamlInSync(component, 'value', 0.0)
        self.assertEqual(['moved'], events)

    def testMovingToEnd(self):
        """ Test firing events and value when the thumb is moved to end.

        """
        component = self.component
        events = self.events

        self.sent_event(self.widget, TestEvents.END)
        self.assertEnamlInSync(component, 'value', 1.0)
        self.assertEqual(['moved'], events)

    def testMovingDownByOneStep(self):
        """ Test firing events and value when the thumb is moved by one step down.

        """
        component = self.component
        events = self.events

        self.sent_event(self.widget, TestEvents.STEP_DOWN)
        self.assertEnamlInSync(component, 'value', 0.4)
        self.assertEqual(['moved'], events)

    def testMovingUpByOneStep(self):
        """ Test firing events and value when the thumb is moved by one step up.

        """
        component = self.component
        events = self.events

        self.sent_event(self.widget, TestEvents.STEP_UP)
        self.assertEnamlInSync(component, 'value', 0.6)
        self.assertEqual(['moved'], events)

    def testMovingDownByOnePage(self):
        """ Test firing events and value when the thumb is moved by one page down.

        """
        component = self.component
        events = self.events

        self.sent_event(self.widget, TestEvents.PAGE_DOWN)
        self.assertEnamlInSync(component, 'value', 0.3)
        self.assertEqual(['moved'], events)

    def testMovingUpByOnePage(self):
        """ Test firing events and value when the thumb is moved by one page up.

        """
        component = self.component
        events = self.events

        self.sent_event(self.widget, TestEvents.PAGE_UP)
        self.assertEnamlInSync(component, 'value', 0.7)
        self.assertEqual(['moved'], events)


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

    @abc.abstractmethod
    def sent_event(self, widget, event):
        """ Sent an event to the Slider programmatically.

        Arguments
        ---------
        widget :
            The widget to sent the event to.

        event :
            The desired event to be proccessed.

        """
        return NotImplemented