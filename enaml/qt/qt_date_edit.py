#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QDateEdit
from .qt_bounded_date import QtBoundedDate


class QtDateEdit(QtBoundedDate):
    """ A Qt4 implementation of an Enaml DateEdit.

    """
    def create(self):
        """ Create the underlying QDateEdit widget.

        """
        self.widget = QDateEdit(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget's attributes.

        """
        super(QtDateEdit, self).initialize(attrs)
        self.set_date_format(attrs['date_format'])
        self.widget.dateChanged.connect(self.on_date_changed)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_message_set_date_format(self, payload):
        """ Handle the 'set-date_format action from the Enaml widget.'

        """
        self.set_date_format(payload['date_format'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def get_date(self):
        """ Return the current date in the control.

        Returns
        -------
        result : QDate
            The current control date as a QDate object.

        """
        return self.widget.date()

    def set_date(self, date):
        """ Set the widget's current date.

        Parameters
        ----------
        date : QDate
            The QDate object to use for setting the date.

        """
        self.widget.setDate(date)

    def set_max_date(self, date):
        """ Set the widget's maximum date.

        Parameters
        ----------
        date : QDate
            The QDate object to use for setting the maximum date.

        """
        self.widget.setMaximumDate(date)

    def set_min_date(self, date):
        """ Set the widget's minimum date.

        Parameters
        ----------
        date : QDate
            The QDate object to use for setting the minimum date.

        """
        self.widget.setMinimumDate(date)

    def set_date_format(self, date_format):
        """ Set the widget's date format.

        Parameters
        ----------
        date_format : str
            A Python time formatting string.
            
        """
        # XXX make sure Python's and Qt's format strings are the 
        # same, or convert between the two.
        self.widget.setDisplayFormat(date_format)

