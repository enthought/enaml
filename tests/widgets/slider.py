#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import (EnamlTestCase, required_method,
                              required_extended_method)
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
    get_value(self, widget)
        Get the Slider's value.

    get_tick_interval(self, widget)
        Get the Slider's tick_interval value.

    get_tick_position(self, widget)
        Get the Slider's tick position style.

    get_orientation(self, widget)
        Get the Slider's orientation.

    get_single_step(self, widget)
        Get the Slider's single step value.

    get_page_step(self, widget)
        Get the Slider's page step value.

    get_tracking(self, widget)
        Get the Slider's tracking status.

    send_event(self, widget, event)
        Send an event to the Slider programmatically.

    """

    def setUp(self):
        """ Set up before the spin box tests.

        """

        enaml = """
Window:
    Panel:
        VGroup:
            Slider slider:
                tick_interval = 0.1
                value = 0.5
                page_step = 2
                moved >> events.append(('moved', msg.new))
                pressed >> events.append('pressed')
                released >> events.append('released')
"""

        self.events = []
        self.view = self.parse_and_create(enaml, events=self.events)
        self.component = self.component_by_id(self.view, 'slider')
        self.widget = self.component.toolkit_widget()

    def test_initial_attributes(self):
        """ Compare the Enaml Slider's attributes with its toolkit widget.

        """
        component = self.component

        self.assertFalse(component.error)
        self.assertIsNone(component.exception)

        self.assertEnamlInSyncExtended(component, 'value', 0.5)
        self.assertEnamlInSync(component, 'tick_interval', 0.1)
        # while the initial value of the tick position is DEFAULT inside the
        # enaml object is converted to NO_TICKS
        self.assertEnamlInSync(component, 'tick_position', TickPosition.NO_TICKS)
        self.assertEnamlInSync(component, 'orientation', Orientation.HORIZONTAL)
        self.assertEnamlInSync(component, 'single_step', 1)
        self.assertEnamlInSync(component, 'page_step', 2)
        self.assertEqual(self.events, [])


    def test_tracking_attribute(self):
        """ Test accesing tracking attribute

        """
        component = self.component

        self.assertEnamlInSync(component, 'tracking', True)

        component.tracking = False
        self.assertEnamlInSync(component, 'tracking', False)
        self.assertEqual(self.events, [])


    def test_value_change(self):
        """Test changing the value programmaticaly.

        """
        component = self.component

        component.value = 1
        self.assertEnamlInSyncExtended(component, 'value', 1)
        component.value = 0.879
        self.assertEnamlInSyncExtended(component, 'value', 0.879)
        self.assertEqual(self.events, [('moved',1), ('moved',0.879)])

    def test_invalid_value_change(self):
        """ Test changing the position with the an invalid value

        when invalid, check that it has not changed the values and the
        errors are updated.
        """
        component = self.component

        component.value = -0.2
        self.assertEnamlInSyncExtended(component, 'value', 0.0)
        component.value = 3
        self.assertEnamlInSyncExtended(component, 'value', 1)


    def test_error_update(self):
        """ Check that errors are assinged

        """
        component = self.component

        component.value = -0.2
        self.assertTrue(component.error)
        self.assertIsInstance(component.exception, ValueError)

        component.value = 3
        self.assertTrue(component.error)
        self.assertIsInstance(component.exception, ValueError)

    def test_error_reset(self):
        """ Check that the error attributes are reset

        """
        component = self.component

        component.value = -0.2
        component.value = 0.3
        self.assertFalse(component.error)
        self.assertIsNone(component.exception)


    def test_orientation_setting(self):
        """ Test changing the widget orientation

        """
        component = self.component

        self.component.orientation = Orientation.VERTICAL
        self.assertEnamlInSync(component, 'orientation', Orientation.VERTICAL)

        self.component.orientation = Orientation.HORIZONTAL
        self.assertEnamlInSync(component, 'orientation', Orientation.HORIZONTAL)

    def test_tick_position_setting(self):
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

    def test_incompatible_tick_position(self):
        """ Test that changing tick position is addapted if the orientation
        is not compatible.

        This is in sync with how the QSlider behaves.

        """

        component = self.component

        component.tick_position = TickPosition.LEFT
        self.assertEnamlInSync(component, 'tick_position', TickPosition.TOP)

        component.tick_position = TickPosition.RIGHT
        self.assertEnamlInSync(component, 'tick_position', TickPosition.BOTTOM)

        self.component.orientation = Orientation.VERTICAL

        component.tick_position = TickPosition.BOTTOM
        self.assertEnamlInSync(component, 'tick_position', TickPosition.RIGHT)

        component.tick_position = TickPosition.TOP
        self.assertEnamlInSync(component, 'tick_position', TickPosition.LEFT)


    def test_changing_orientaion_tick_policy(self):
        """ Test that the ticks follow the orientation changes

        """
        component = self.component

        component.tick_position = TickPosition.BOTTOM
        self.component.orientation = Orientation.VERTICAL
        self.assertEnamlInSync(component, 'tick_position', TickPosition.RIGHT)
        component.tick_position = TickPosition.LEFT
        self.component.orientation = Orientation.HORIZONTAL
        self.assertEnamlInSync(component, 'tick_position', TickPosition.TOP)


    def test_pressing_the_thumb(self):
        """ Test firing events when the thumb is pressed down.

        """
        events = self.events

        self.send_event(self.widget, TestEvents.PRESSED)
        self.assertEqual(['pressed'], events)

    def test_releasing_the_thumb(self):
        """ Test firing events when the thumb is released.

        """
        events = self.events

        self.send_event(self.widget, TestEvents.RELEASED)
        self.assertEqual([], events)

        self.send_event(self.widget, TestEvents.PRESSED)
        self.send_event(self.widget, TestEvents.RELEASED)
        self.assertEqual(['pressed', 'released'], events)

    def test_moving_the_thumb_programmaticaly(self):
        """ Test firing events when the thumb is moved (programmatically).

        """
        component = self.component
        events = self.events

        component.value = 0.3
        self.assertEqual(events, [('moved', 0.3)])

    def test_move_to_home(self):
        """ Test firing events and value when the thumb is moved to home.

        """
        component = self.component
        events = self.events

        self.send_event(self.widget, TestEvents.HOME)
        self.assertEnamlInSyncExtended(component, 'value', 0.0)
        self.assertEqual(events, [('moved', 0.0)])

    def test_move_to_end(self):
        """ Test firing events and value when the thumb is moved to end.

        """
        component = self.component
        events = self.events

        self.send_event(self.widget, TestEvents.END)
        self.assertEnamlInSyncExtended(component, 'value', 1.0)
        self.assertEqual(events, [('moved', 1.0)])

    def test_move_down_by_one_step(self):
        """ Test firing events and value when the thumb is moved by one step down.

        """
        component = self.component
        events = self.events

        self.send_event(self.widget, TestEvents.STEP_DOWN)
        self.assertEnamlInSyncExtended(component, 'value', 0.4)
        self.assertEqual(events, [('moved', 0.4)])

    def test_move_up_by_one_step(self):
        """ Test firing events and value when the thumb is moved by one step up.

        """
        component = self.component
        events = self.events

        self.send_event(self.widget, TestEvents.STEP_UP)
        self.assertEnamlInSyncExtended(component, 'value', 0.6)
        self.assertEqual(events, [('moved', 0.6)])

    def test_move_down_by_one_page(self):
        """ Test firing events and value when the thumb is moved by one page down.

        """
        component = self.component
        events = self.events

        self.send_event(self.widget, TestEvents.PAGE_DOWN)
        self.assertEnamlInSyncExtended(component, 'value', 0.3)
        self.assertEqual(events, [('moved', 0.3)])

    def test_move_up_by_one_page(self):
        """ Test firing events and value when the thumb is moved by one page up.

        """
        component = self.component
        events = self.events

        self.send_event(self.widget, TestEvents.PAGE_UP)
        self.assertEnamlInSyncExtended(component, 'value', 0.7)
        self.assertEqual(events, [('moved', 0.7)])

    #--------------------------------------------------------------------------
    # test special initialization
    #--------------------------------------------------------------------------

    def test_using_log_converter(self):
        """ Test slider when using the log converter

        """
        enaml = """
from enaml.converters import SliderLogConverter
Window:
    Panel:
        VGroup:
            Slider slider:
                tick_interval = 0.1
                value = 1.0
                convert = SliderLogConverter()
                page_step = 2
                moved >> events.append(('moved', msg.new))
                pressed >> events.append('pressed')
                released >> events.append('released')
"""

        self.events = []
        view = self.parse_and_create(enaml, events=self.events)
        component = self.component_by_id(view, 'slider')
        self.assertEnamlInSyncExtended(component, 'value', 1.0)


    #--------------------------------------------------------------------------
    # absrtact methods
    #--------------------------------------------------------------------------

    @required_extended_method
    def get_value(self, component, widget):
        """ Get the Slider's value.

        .. note:: please note that this attribute requires the extended
            signature.
        """
        pass

    @required_method
    def get_tick_interval(self, widget):
        """ Get the Slider's tick_interval value.

        """
        pass

    @required_method
    def get_tick_position(self, widget):
        """ Get the Slider's tick position style.

        """
        pass

    @required_method
    def get_orientation(self, widget):
        """ Get the Slider's orientation.

        """
        pass

    @required_method
    def get_single_step(self, widget):
        """ Get the Slider's single step value.

        """
        pass

    @required_method
    def get_page_step(self, widget):
        """ Get the Slider's page step value.

        """
        pass

    @required_method
    def get_tracking(self, widget):
        """ Get the Slider's tracking status.

        """
        pass

    @required_method
    def send_event(self, widget, event):
        """ Send an event to the Slider programmatically.

        Arguments
        ---------
        widget :
            The widget to send the event to.

        event :
            The desired event to be proccessed.

        """
        pass