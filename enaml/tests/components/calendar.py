#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import date

from traits.api import TraitError

from .enaml_test_case import EnamlTestCase, required_method


class TestCalendar(EnamlTestCase):
    """ Logic for testing calendars.

    Toolkit testcases need to provide the following functions

    Abstract Methods
    ----------------
    get_date(self, widget)
        Get a calendar's active date.

    get_min_date(self, widget)
        Get a calendar's minimum date attribute.

    get_max_date(self, widget)
        Get a calendar's maximum date attribute.

    activate_date(self, widget, date)
        Fire an event to indicate that a date was activated.

    select_date(self, widget, date)
        Fire an event to indicate that a date was selected.

    """

    def setUp(self):
        """ Set up before the calendar tests

        """

        source = """
enamldef MainView(MainWindow):
    attr events
    Calendar:
        name = 'cal'
        selected :: events.append(('selected', event.new))
        activated :: events.append(('activated', event.new))
"""

        self.events = []
        self.view = self.parse_and_create(source, events=self.events)
        self.component = self.component_by_name(self.view, 'cal')
        self.widget = self.component.toolkit_widget

    def test_initial_value(self):
        """ Test the initial attributes of the calendar.

        """
        component = self.component

        self.assertEnamlInSync(component, 'date', date.today())
        self.assertEnamlInSync(component, 'min_date', date(1752, 9, 14))
        self.assertEnamlInSync(component, 'max_date', date(7999, 12, 31))
        self.assertEqual(self.events, [])

    def test_change_min_date(self):
        """ Test changing the minimum date.

        """
        component = self.component
        new_minimum = date(2000,1,1)
        component.min_date = new_minimum
        self.assertEnamlInSync(component, 'min_date', new_minimum)

    def test_change_max_date(self):
        """ Test changing the maximum date.

        """
        component = self.component
        new_maximum = date(2005,1,1)
        component.max_date = new_maximum
        self.assertEnamlInSync(component, 'max_date', new_maximum)

    def test_change_date_in_enaml(self):
        """ Test changing the current date through the component.

        """
        component = self.component
        new_date = date(2007,10,9)
        component.date = new_date
        self.assertEnamlInSync(component, 'date', new_date)
        self.assertEqual(self.events, [])

    def test_invalid_min_date(self):
        """ Test changing to an invalid date below the min range.

        """
        component = self.component
        min_date = date(2000,2,3)
        component.min_date = min_date
        with self.assertRaises(TraitError):
            component.date = date(2000,1,1)
        self.assertEnamlInSync(component, 'date', date.today())
        self.assertEqual(self.events, [])

    def test_invalid_max_date(self):
        """ Test changing to an invalid date above the max range.

        """
        component = self.component
        component.date = date(2011,10,9)
        self.assertEqual(self.events, [])
        max_date = date(2014,2,3)
        component.max_date = max_date
        with self.assertRaises(TraitError):
            component.date = date(2016,10,9)
        self.assertEnamlInSync(component, 'date', date(2011,10,9))
        self.assertEqual(self.events, [])

    def test_select_date_in_ui(self):
        """ Test changing the current date thought the ui

        """
        component = self.component
        widget = self.widget
        new_date = date(2007,10,9)
        self.select_date(widget, new_date)
        self.assertEqual(self.get_date(widget), new_date)
        # make sure that the component is not updated when selected is fired
        self.assertEqual(component.date, date.today())
        self.assertEqual(self.events, [('selected', new_date)])

    def test_activate_date_in_ui(self):
        """ Test activating the current date thought the ui

        """
        component = self.component
        widget = self.widget
        new_date = date(2007,10,9)
        self.select_date(widget, new_date)
        self.activate_date(self.widget, new_date)
        self.assertEnamlInSync(component, 'date', new_date)
        self.assertEqual(self.events, [('selected', new_date),
                                       ('activated', new_date)])

    def test_change_maximum_and_date(self):
        """ Test setting maximum while the date is out of range.

        """
        component = self.component
        component.date = date(2007,10,9)
        component.max_date = date(2006,5,9)
        self.assertEnamlInSync(component, 'date', date(2006,5,9))
        self.assertEqual(self.events, [])

    def test_change_minimum_and_date(self):
        """ Test setting minimum while the date is out of range.

        """
        component = self.component
        component.date = date(2007,10,9)
        component.min_date = date(2010,5,9)
        self.assertEnamlInSync(component, 'date', date(2010,5,9))
        self.assertEqual(self.events, [])

    def test_change_range_invalid(self):
        """ Test setting minimum > maximum.

        """
        component = self.component
        component.min_date = date(2010,5,9)
        with self.assertRaises(TraitError):
            component.max_date = date(2006,5,9)

        component.max_date = date(2034,12,10)
        with self.assertRaises(TraitError):
            component.min_date = date(2034,12,14)

    #--------------------------------------------------------------------------
    # Special initialization tests
    #--------------------------------------------------------------------------
    def test_initial_too_early(self):
        """ Check initialization with an invalid early date is corrected.

        .. todo:: avoid using the enaml source

        """
        enaml_source = """
import datetime
enamldef MainView(MainWindow):
    attr events
    Calendar:
        name = 'cal'
        date = datetime.date(1980, 1, 1)
        min_date = datetime.date(1990, 1, 1)
        max_date = datetime.date(2000, 1, 1)
        selected :: events.append(('selected', event.new))
        activated :: events.append(('activated', event.new))

"""
        events = []
        with self.assertRaises(TraitError):
            self.parse_and_create(enaml_source, events=events)

    def test_initial_too_late(self):
        """ Check initialization with an invalid late date is corrected.

        .. todo:: avoid using the enaml source

        """
        enaml = """
import datetime
enamldef MainView(MainWindow):
    attr events
    Calendar:
        name = 'cal'
        date = datetime.date(2010, 1, 1)
        min_date = datetime.date(1990, 1, 1)
        max_date = datetime.date(2000, 1, 1)
        selected :: events.append(('selected', event.new))
        activated :: events.append(('activated', event.new))
"""
        events = []
        with self.assertRaises(TraitError):
            self.parse_and_create(enaml, events=events)

    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @required_method
    def get_date(self, widget):
        """ Get a calendar's active date.

        """
        pass

    @required_method
    def get_min_date(self, widget):
        """ Get a calendar's minimum date attribute.

        """
        pass

    @required_method
    def get_max_date(self, widget):
        """ Get a calendar's maximum date attribute.

        """
        pass

    @required_method
    def activate_date(self, widget):
        """ Fire an event to indicate that a date was activated.

        """
        pass

    @required_method
    def select_date(self, widget, date):
        """ Fire an event to indicate that a date was selected.

        """
        pass

