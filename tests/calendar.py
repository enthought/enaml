#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import date

from .enaml_test_case import EnamlTestCase, required_method


class TestCalendar(EnamlTestCase):
    """ Logic for testing calendars.

    Tooklit testcases need to provide the following functions

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

    enaml = """
import datetime
Window:
    Panel:
        VGroup:
            Calendar cal:
                selected >> events.append('selected')
                activated >> events.append('activated')
"""

    def setUp(self):
        """ Set up before the calendar tests

        """
        super(TestCalendar, self).setUp()
        component = self.widget_by_id('cal')
        self.widget = component.toolkit_widget()
        self.component = component

    def test_initial_value(self):
        """ Test the initial attributes of the calendar.

        """
        component = self.component

        self.assertEnamlInSync(component, 'date', date.today())
        self.assertEnamlInSync(component, 'minimum_date', date(1752, 9, 14))
        self.assertEnamlInSync(component, 'maximum_date', date(7999, 12, 31))
        self.assertEqual(self.events, [])

    def test_activated_fired(self):
        """ Test that the 'activated' event fires properly.

        """
        self.activate_date(self.widget, date(1970, 2, 1))
        self.assertEqual(self.events, ['activated'])

    def test_initial_too_early(self):
        """ Check initialization with an invalid early date is corrected.

        """
        self.enaml = """
import datetime
Window:
    Panel:
        VGroup:
            Calendar cal:
                date = datetime.date(1980, 1, 1)
                minimum_date = datetime.date(1990, 1, 1)
                maximum_date = datetime.date(2000, 1, 1)
"""
        self.setUp()
        component = self.component
        self.assertEnamlInSync(component, 'date', date(1990, 1, 1))
        self.assertEqual(self.events, [])

    def test_initial_too_late(self):
        """ Check initialization with an invalid late date is corrected.

        """
        self.enaml = """
import datetime
Window:
    Panel:
        VGroup:
            Calendar cal:
                date = datetime.date(2010, 1, 1)
                minimum_date = datetime.date(1990, 1, 1)
                maximum_date = datetime.date(2000, 1, 1)
"""
        self.setUp()
        component = self.component
        self.assertEnamlInSync(component, 'date', date(2000, 1, 1))
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
        self.assertEqual(self.events, ['selected'])


    def test_invalid_max_date(self):
        """ Test changing to an invalid date above the max range.

        When an invalid (out of range) date is assinged the widget should
        truncate it in range.

        """
        component = self.component

        component.date = date(2011,10,9)
        self.assertEqual(self.events, ['selected'])
        max_date = date(2014,2,3)
        component.maximum_date = max_date
        component.date = date(2016,10,9)
        self.assertEnamlInSync(component, 'date', max_date)
        self.assertEqual(self.events, ['selected']*2)

    def test_invalid_min_date(self):
        """ Test changing to an invalid date below the min range.

        When an invalid (out of range) date is assinged the widget should
        truncate it in range.

        """
        component = self.component
        min_date = date(2000,2,3)
        component.minimum_date = min_date
        component.date = date(2000,1,1)
        self.assertEnamlInSync(component, 'date', min_date)
        self.assertEqual(self.events, ['selected'])


    def test_select_date_in_ui(self):
        """ Test changing the current date thought the ui

        """
        component = self.component
        widget = self.widget
        new_date = date(2007,10,9)
        self.select_date(widget, new_date)
        self.assertEnamlInSync(component, 'date', new_date)
        self.assertEqual(self.events, ['selected'])

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
    def activate_date(self, widget, date):
        """ Fire an event to indicate that a date was activated.

        """
        pass

    @required_method
    def select_date(self, widget, date):
        """ Fire an event to indicate that a date was selected.

        """
        pass
