#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QDateTimeEdit
from .qt_bounded_datetime import QtBoundedDatetime


class QtDatetimeSelector(QtBoundedDatetime):
    """ A Qt implementation of a datetime edit

    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QDateTimeEdit(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget's attributes

        """
        super(QtDatetimeSelector, self).initialize(attrs)
        self.set_datetime_format(attrs['datetime_format'])
        self.widget.dateTimeChanged.connect(self.on_datetime_changed)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_datetime_format(self, content):
        """ Handle the 'set_datetime_format' action from the Enaml
        widget.

        """
        self.set_datetime_format(content['datetime_format'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def get_datetime(self):
        """ Return the current datetime in the control.

        Returns
        -------
        result : QDateTime
            The current control datetime as a QDateTime object.

        """
        return self.widget.dateTime()

    def set_datetime(self, datetime):
        """ Set the widget's current datetime.

        Parameters
        ----------
        datetime : QDateTime
            The QDateTime object to use for setting the datetime.

        """
        self.widget.setDateTime(datetime)

    def set_max_datetime(self, datetime):
        """ Set the widget's maximum datetime.

        Parameters
        ----------
        datetime : QDateTime
            The QDateTime object to use for setting the maximum datetime.

        """
        self.widget.setMaximumDateTime(datetime)

    def set_min_datetime(self, datetime):
        """ Set the widget's minimum datetime.

        Parameters
        ----------
        datetime : QDateTime
            The QDateTime object to use for setting the minimum datetime.

        """
        self.widget.setMinimumDateTime(datetime)

    def set_datetime_format(self, datetime_format):
        """ Set the widget's datetime format.

        Parameters
        ----------
        datetime_format : str
            A Python time formatting string.

        """
        # XXX make sure Python's and Qt's format strings are the 
        # same, or convert between the two.
        self.widget.setDisplayFormat(datetime_format)

