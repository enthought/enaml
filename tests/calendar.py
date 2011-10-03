#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import abc
from datetime import date

from .enaml_test_case import EnamlTestCase


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

    __metaclass__  = abc.ABCMeta

    enaml = """
import datetime
Window:
    Panel:
        VGroup:
            Calendar cal:
                date = datetime.date(1970, 2, 1)
                minimum_date = datetime.date(1970, 1, 1)
                maximum_date = datetime.date(1970, 2, 15)
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
        widget = self.widget
        component = self.component

        self.assertEqual(self.get_date(widget), component.date)
        self.assertEqual(self.get_minimum_date(widget), component.minimum_date)
        self.assertEqual(self.get_maximum_date(widget), component.maximum_date)

    def test_selected_fired(self):
        """ Test that the 'selected' event fires properly.

        """
        self.select_date(self.widget, date(1970, 2, 1))
        self.assertEqual(self.events, ['selected'])

    def test_activated_fired(self):
        """ Test that the 'activated' event fires properly.

        """
        self.activate_date(self.widget, date(1970, 2, 1))
        self.assertEqual(self.events, ['activated'])

    def test_initial_too_early(self):
        """ Check that an invalid date is corrected (value below the minimum).

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
        self.assertEqual(component.date, component.minimum_date)

    def test_initial_too_late(self):
        """ Check that an invalid date is corrected (value above the maximum).

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
        self.assertEqual(component.date, component.maximum_date)

    #--------------------------------------------------------------------------
    # absrtact methods
    #--------------------------------------------------------------------------

    @abc.abstractmethod
    def get_date(self, widget):
        """ Get a calendar's active date.

        """
        return NotImplemented

    @abc.abstractmethod
    def get_minimum_date(self, widget):
        """ Get a calendar's minimum date attribute.

        """
        return NotImplemented

    @abc.abstractmethod
    def get_maximum_date(self, widget):
        """ Get a calendar's maximum date attribute.

        """
        return NotImplemented

    @abc.abstractmethod
    def activate_date(self, widget, date):
        """ Fire an event to indicate that a date was activated.

        """
        return NotImplemented

    @abc.abstractmethod
    def select_date(self, widget, date):
        """ Fire an event to indicate that a date was selected.

        """
        return NotImplemented
