#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt, QDate
from .qt_constraints_widget import QtConstraintsWidget


def as_qdate(iso_date):
    """ Convert an iso date string to a QDate

    """
    return QDate.fromString(iso_date, Qt.ISODate)


def as_iso_date(qdate):
    """ Convert a QDate object into and iso date string.

    """
    return qdate.toString(Qt.ISODate)


class QtBoundedDate(QtConstraintsWidget):
    """ A base class for date widgets.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def initialize(self, attrs):
        """ Initialize the attributes of the date widget.

        """
        super(QtBoundedDate, self).initialize(attrs)
        self.set_min_date(as_qdate(attrs['minimum']))
        self.set_max_date(as_qdate(attrs['maximum']))
        self.set_date(as_qdate(attrs['date']))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_date(self, payload):
        """ Handle the 'set-date' action from the Enaml widget.
    
        """
        self.set_date(as_qdate(payload['date']))

    def on_message_set_minimum(self, payload):
        """ Hanlde the 'set-minimum' action from the Enaml widget.

        """
        self.set_min_date(as_qdate(payload['minimum']))

    def on_message_set_maximum(self, payload):
        """ Handle the 'set-maximum' action from the Enaml widget.

        """
        self.set_max_date(as_qdate(payload['maximum']))

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_date_changed(self):
        """ A signal handler to connect to the date changed signal of 
        the underlying widget.

        This will convert the QDate to iso format and send the Enaml
        widget the 'event-changed' action.

        """
        qdate = self.get_date()
        payload = {
            'action': 'event-changed', 'date': as_iso_date(qdate),
        }
        self.send_message(payload)

    #--------------------------------------------------------------------------
    # Abstract Methods
    #--------------------------------------------------------------------------
    def get_date(self):
        """ Return the current date in the control.

        Returns
        -------
        result : QDate
            The current control date as a QDate object.

        """
        raise NotImplementedError

    def set_date(self, date):
        """ Set the widget's current date.

        Parameters
        ----------
        date : QDate
            The QDate object to use for setting the date.

        """
        raise NotImplementedError

    def set_max_date(self, date):
        """ Set the widget's maximum date.

        Parameters
        ----------
        date : QDate
            The QDate object to use for setting the maximum date.

        """
        raise NotImplementedError

    def set_min_date(self, date):
        """ Set the widget's minimum date.

        Parameters
        ----------
        date : QDate
            The QDate object to use for setting the minimum date.

        """
        raise NotImplementedError

