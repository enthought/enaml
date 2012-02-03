#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import datetime as python_datetime

from traits.api import TraitError

from .enaml_test_case import EnamlTestCase, required_method


class TestDatetimeEdit(EnamlTestCase):
    """ Logic for testing the date time edit components.

    Tooklit testcases need to provide the following functions

    Abstract Methods
    ----------------
    get_datetime(self, widget)
        Get the toolkits widget's active datetime.

    get_min_datetime(self, widget)
        Get the toolkits widget's maximum datetime attribute.

    get_max_datetime(self, widget)
        Get the toolkits widget's minimum datetime attribute.

    change_datetime(self, widget, date)
        Simulate a change datetime action at the toolkit widget.

    get_datetime_as_string(self, widget)
        Get the toolkits widget's active datetime as a string.

    """

    def setUp(self):
        """ Set up for the TimeEdit testcases

        """

        enaml_source = """
from datetime import datetime as python_datetime
enamldef MainView(MainWindow):
    attr events
    DatetimeEdit:
        name = 'test'
        datetime = python_datetime(2001, 4, 3, 8, 45, 32, 23000)
        datetime_changed :: events.append(('datetime_changed', event.new))
"""

        self.default_datetime = python_datetime(2001, 4, 3, 8, 45, 32, 23000)
        self.events = []
        self.view = self.parse_and_create(enaml_source, events=self.events)
        self.component = self.component_by_name(self.view, 'test')
        self.widget = self.component.toolkit_widget

    def test_initialization_values(self):
        """ Test the initial attributes of the date edit component.

        """
        component = self.component

        self.assertEnamlInSync(component, 'datetime',
                               python_datetime(2001, 4, 3, 8, 45, 32, 23000))
        self.assertEnamlInSync(component, 'min_datetime',
                               python_datetime(1752,9,14,0,0,0,0))
        self.assertEnamlInSync(component, 'max_datetime',
                               python_datetime(7999, 12, 31, 23, 59, 59, 999000))
        self.assertEqual(self.events, [])

    def test_change_max_datetime(self):
        """ Test changing the maximum datetime.

        """
        component = self.component
        new_maximum = python_datetime(2005,1,1)
        component.max_datetime = new_maximum
        self.assertEnamlInSync(component, 'max_datetime', new_maximum)
        self.assertEqual(self.events, [])

    def test_change_min_datetime(self):
        """ Test changing the minimum datetime.

        """
        component = self.component
        new_minimum = python_datetime(2000,1,1)
        component.min_datetime = new_minimum
        self.assertEnamlInSync(component, 'min_datetime', new_minimum)
        self.assertEqual(self.events, [])

    def test_change_maximum_and_datetime(self):
        """ Test setting maximum while the datetime is out of range.

        """
        component = self.component
        component.datetime = python_datetime(2007,10,9)
        component.max_datetime = python_datetime(2006,5,9)
        self.assertEnamlInSync(component, 'datetime', python_datetime(2006,5,9))
        self.assertEqual(self.events, [])

    def test_change_minimum_and_datetime(self):
        """ Test setting minimum while the datetime is out of range.

        """
        component = self.component
        component.datetime = python_datetime(2007,10,9)
        component.min_datetime = python_datetime(2010,5,9)
        self.assertEnamlInSync(component, 'datetime', python_datetime(2010,5,9))
        self.assertEqual(self.events, [])

    def test_change_datetime_in_enaml(self):
        """ Test changing the current datetime through the component.

        """
        component = self.component
        new_datetime = python_datetime(2007,10,9)
        component.datetime = new_datetime
        self.assertEnamlInSync(component, 'datetime', new_datetime)
        self.assertEqual(self.events, [])

    def test_change_datetime_in_ui(self):
        """ Test changing the current datetime thought the ui

        """
        component = self.component
        widget = self.widget
        new_datetime = python_datetime(2007,10,9)
        self.change_datetime(widget, new_datetime)
        self.assertEnamlInSync(component, 'datetime', new_datetime)
        self.assertEqual(self.events, [('datetime_changed', new_datetime)])

    def test_invalid_min_datetime(self):
        """ Test changing to an invalid datetime below the min range.

        """
        component = self.component
        min_datetime = python_datetime(2000,2,3)
        component.min_datetime = min_datetime
        with self.assertRaises(TraitError):
            component.datetime = python_datetime(2000,1,1)
        self.assertEnamlInSync(component, 'datetime', self.default_datetime)

    def test_invalid_max_datetime(self):
        """ Test changing to an invalid datetime above the max range.

        """
        component = self.component
        init_datetime = python_datetime(2011,10,9)
        component.datetime = init_datetime
        self.assertEqual(self.events, [])
        max_datetime = python_datetime(2014,2,3)
        component.max_datetime = max_datetime
        with self.assertRaises(TraitError):
            component.datetime = python_datetime(2016,10,9)
        self.assertEnamlInSync(component, 'datetime', init_datetime)
        self.assertEqual(self.events, [])

    def test_set_format(self):
        """ Test setting the output format

        """
        component = self.component
        widget = self.widget
        component.datetime_format = 'MMM dd yyyy hh:mm'
        test_datetime = python_datetime(2007,10,9, 2, 34, 12,2000)
        component.datetime = test_datetime
        widget_string = self.get_datetime_as_string(widget)
        formated_date = unicode(test_datetime.strftime('%b %d %Y %H:%M'), encoding='utf-8')
        self.assertEqual(widget_string, formated_date)
        self.assertEqual(self.events, [])

    def test_change_range_invalid(self):
        """ Test setting minimum > maximum.

        """
        component = self.component
        component.min_datetime = python_datetime(2010,5,9)
        with self.assertRaises(TraitError):
            component.max_datetime = python_datetime(2006,5,9)

        component.max_datetime = python_datetime(2034,12,10)
        with self.assertRaises(TraitError):
            component.min_date = python_datetime(2034,12,14)

    #--------------------------------------------------------------------------
    # Special initialization tests
    #--------------------------------------------------------------------------
    def test_initial_too_early(self):
        """ Check initialization with an invalid early datetime is corrected.

        .. todo:: avoid using the enaml source

        """
        enaml_source = """
from datetime import datetime as python_datetime
enamldef MainView(MainWindow):
    attr events
    DatetimeEdit:
        name = 'test'
        datetime = python_datetime(1980, 1, 1, 23, 10, 34)
        min_datetime = python_datetime(1990, 1, 1)
        max_datetime = python_datetime(2000, 1, 1)
        datetime_changed :: events.append(('datetime_changed', event.new))
"""
        events = []
        with self.assertRaises(TraitError):
            self.parse_and_create(enaml_source, events=events)

    def test_initial_too_late(self):
        """ Check initialization with an invalid late datetime is corrected.

        .. todo:: avoid using the enaml source

        """
        enaml_source = """
from datetime import datetime as python_datetime
enamldef MainView(MainWindow):
    attr events
    DatetimeEdit:
        name = 'test'
        datetime = python_datetime(2010, 1, 1, 9, 12, 34, 14234)
        min_datetime = python_datetime(1990, 1, 1)
        max_datetime = python_datetime(2000, 1, 1)
        datetime_changed :: events.append(('datetime_changed', event.new))
"""
        events = []
        with self.assertRaises(TraitError):
            self.parse_and_create(enaml_source, events=events)

    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @required_method
    def get_datetime(self, widget):
        """  Get the toolkits widget's active datetime.

        """
        pass

    @required_method
    def get_min_datetime(self, widget):
        """  Get the toolkits widget's maximum datetime attribute.

        """
        pass

    @required_method
    def get_max_datetime(self, widget):
        """ Get the toolkits widget's minimum datetime attribute.

        """
        pass

    @required_method
    def change_datetime(self, widget, date):
        """ Simulate a change datetime action at the toolkit widget.

        """
        pass

    @required_method
    def get_datetime_as_string(self, widget):
        """  Get the toolkits widget's active datetime as a string.

        """
        pass

