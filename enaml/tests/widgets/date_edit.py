#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import date

from traits.api import TraitError

from .enaml_test_case import EnamlTestCase, required_method


class TestDateEdit(EnamlTestCase):
    """ Logic for testing the date edit components.

    Tooklit testcases need to provide the following functions

    Abstract Methods
    ----------------
    get_date(self, widget)
        Get the toolkits widget's active date.

    get_minimum_date(self, widget)
        Get the toolkits widget's minimum date attribute.

    get_maximum_date(self, widget)
        Get the toolkits widget's maximum date attribute.

    change_date(self, widget, date)
        Simulate a change date action at the toolkit widget.

    get_date_as_string(self, widget)
        Get the toolkits widget's active date as a string.

    """

    def setUp(self):
        """ Set up before the date_edit tests

        """

        enaml = """
Window:
    Panel:
        VGroup:
            DateEdit test:
                date_changed >> events.append('date_changed')
"""

        self.events = []
        self.view = self.parse_and_create(enaml, events=self.events)
        self.component = self.component_by_id(self.view, 'test')
        self.widget = self.component.toolkit_widget()

    def test_initialization_values(self):
        """ Test the initial attributes of the date edit component.

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
        self.assertEqual(self.events, ['date_changed'])

    def test_change_date_in_ui(self):
        """ Test changing the current date thought the ui

        """
        component = self.component
        widget = self.widget
        new_date = date(2007,10,9)
        self.change_date(widget, new_date)
        self.assertEnamlInSync(component, 'date', new_date)
        self.assertEqual(self.events, ['date_changed'])

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

    def test_invalid_max_date(self):
        """ Test changing to an invalid date above the max range.

        """
        component = self.component
        component.date = date(2011,10,9)
        self.assertEqual(self.events, ['date_changed'])
        max_date = date(2014,2,3)
        component.maximum_date = max_date
        with self.assertRaises(TraitError):
            component.date = date(2016,10,9)
        self.assertEnamlInSync(component, 'date', date(2011,10,9))
        self.assertEqual(self.events, ['date_changed'])

    def test_set_format(self):
        """ Test setting the output format

        """
        component = self.component
        widget = self.widget

        component.format = 'MMM dd yyyy'
        component.date = date(2007,10,9)
        widget_string = self.get_date_as_string(widget)
        self.assertEqual(widget_string, u'Oct 09 2007')


    #--------------------------------------------------------------------------
    # Special initialization tests
    #--------------------------------------------------------------------------

    def test_initial_too_late(self):
        """ Check initialization with an invalid late date is corrected.

        """
        enaml = """
import datetime
Window:
    Panel:
        VGroup:
            DateEdit test:
                date = datetime.date(2010, 1, 1)
                minimum_date = datetime.date(1990, 1, 1)
                maximum_date = datetime.date(2000, 1, 1)
                date_changed >> events.append('date_changed')
"""
        events = []
        with self.assertRaises(TraitError):
            view = self.parse_and_create(enaml, events=events)


    def test_initial_too_early(self):
        """ Check initialization with an invalid early date is corrected.

        """

        enaml = """
import datetime
Window:
    Panel:
        VGroup:
            DateEdit test:
                date = datetime.date(1980, 1, 1)
                minimum_date = datetime.date(1990, 1, 1)
                maximum_date = datetime.date(2000, 1, 1)
                date_changed >> events.append('date_changed')
"""

        events = []
        with self.assertRaises(TraitError):
            view = self.parse_and_create(enaml, events=events)

    #--------------------------------------------------------------------------
    # absrtact methods
    #--------------------------------------------------------------------------

    @required_method
    def get_date(self, widget):
        """  Get the toolkits widget's active date.

        """
        pass

    @required_method
    def get_minimum_date(self, widget):
        """  Get the toolkits widget's maximum date attribute.

        """
        pass

    @required_method
    def get_maximum_date(self, widget):
        """ Get the toolkits widget's minimum date attribute.

        """
        pass

    @required_method
    def change_date(self, widget, date):
        """ Simulate a change date action at the toolkit widget.

        """
        pass

    @required_method
    def get_date_as_string(self, widget):
        """  Get the toolkits widget's active date as a string.

        """
        pass
