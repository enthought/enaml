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

    get_minimum_date(self, widget)
        Get a calendar's minimum date attribute.

    get_maximum_date(self, widget)
        Get a calendar's maximum date attribute.

    activate_date(self, widget, date)
        Fire an event to indicate that a date was activated.

    select_date(self, widget, date)
        Fire an event to indicate that a date was selected.

    """

    def setUp(self):
        """ Set up before the calendar tests

        """

        enaml = """
Window:
    Panel:
        VGroup:
            Calendar cal:
                selected >> events.append(('selected', msg.new))
                activated >> events.append(('activated', msg.new))
"""

        self.events = []
        self.view = self.parse_and_create(enaml, events=self.events)
        self.component = self.component_by_id(self.view, 'cal')
        self.widget = self.component.toolkit_widget()

    def test_initial_value(self):
        """ Test the initial attributes of the calendar.

        """
        component = self.component

        self.assertEnamlInSync(component, 'date', date.today())
        self.assertEnamlInSync(component, 'minimum_date', date(1752, 9, 14))
        self.assertEnamlInSync(component, 'maximum_date', date(7999, 12, 31))
        self.assertEqual(self.events, [])

    def test_change_minimum_date(self):
        """ Test changing the minimum date.

        """
        component = self.component
        new_minimum = date(2000,1,1)
        component.minimum_date = new_minimum
        self.assertEnamlInSync(component, 'minimum_date', new_minimum)

    def test_change_maximum_date(self):
        """ Test changing the maximum date.

        """
        component = self.component
        new_maximum = date(2005,1,1)
        component.maximum_date = new_maximum
        self.assertEnamlInSync(component, 'maximum_date', new_maximum)

    def test_change_date_in_enaml(self):
        """ Test changing the current date through the component.

        """
        component = self.component
        new_date = date(2007,10,9)
        component.date = new_date
        self.assertEnamlInSync(component, 'date', new_date)
        self.assertEqual(self.events, [('selected', new_date)])


    def test_invalid_max_date(self):
        """ Test changing to an invalid date above the max range.

        """
        component = self.component

        component.date = date(2011,10,9)
        self.assertEqual(self.events, [('selected', date(2011,10,9))])
        max_date = date(2014,2,3)
        component.maximum_date = max_date
        with self.assertRaises(TraitError):
            component.date = date(2016,10,9)
        self.assertEnamlInSync(component, 'date', date(2011,10,9))
        self.assertEqual(len(self.events), 1)

    def test_invalid_min_date(self):
        """ Test changing to an invalid date below the min range.

        """
        component = self.component
        min_date = date(2000,2,3)
        component.minimum_date = min_date
        with self.assertRaises(TraitError):
            component.date = date(2000,1,1)
        self.assertEnamlInSync(component, 'date', date.today())
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


    #--------------------------------------------------------------------------
    # Special initialization tests
    #--------------------------------------------------------------------------

    def test_initial_too_early(self):
        """ Check initialization with an invalid early date is corrected.

        .. todo:: avoid using the enaml source

        """
        enaml = """
import datetime
Window:
    Panel:
        VGroup:
            Calendar cal:
                date = datetime.date(1980, 1, 1)
                minimum_date = datetime.date(1990, 1, 1)
                maximum_date = datetime.date(2000, 1, 1)
                selected >> events.append(('selected', msg.new))
                activated >> events.append(('activated', msg.new))

"""
        events = []
        with self.assertRaises(TraitError):
            view = self.parse_and_create(enaml, events=events)

    def test_initial_too_late(self):
        """ Check initialization with an invalid late date is corrected.

        .. todo:: avoid using the enaml source

        """
        enaml = """
import datetime
Window:
    Panel:
        VGroup:
            Calendar cal:
                date = datetime.date(2010, 1, 1)
                minimum_date = datetime.date(1990, 1, 1)
                maximum_date = datetime.date(2000, 1, 1)
                selected >> events.append(('selected', msg.new))
                activated >> events.append(('activated', msg.new))
"""
        events = []
        with self.assertRaises(TraitError):
            view = self.parse_and_create(enaml, events=events)

    #--------------------------------------------------------------------------
    # absrtact methods
    #--------------------------------------------------------------------------

    @required_method
    def get_date(self, widget):
        """ Get a calendar's active date.

        """
        pass

    @required_method
    def get_minimum_date(self, widget):
        """ Get a calendar's minimum date attribute.

        """
        pass

    @required_method
    def get_maximum_date(self, widget):
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
