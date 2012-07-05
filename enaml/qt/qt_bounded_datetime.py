#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt, QDateTime
from .qt_constraints_widget import QtConstraintsWidget


def as_qdatetime(iso_datetime):
    """ Convert an iso datetime string to a QDateTime.

    """
    return QDateTime.fromString(iso_datetime, Qt.ISODate)


def as_iso_datetime(qdatetime):
    """ Convert a QDateTime object into an iso datetime string.

    """
    return qdatetime.toString(Qt.ISODate)


class QtBoundedDatetime(QtConstraintsWidget):
    """ A base class for datetime widgets.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def initialize(self, attrs):
        """ Initialize the attributes of the date widget.

        """
        super(QtBoundedDatetime, self).initialize(attrs)
        self.set_min_datetime(as_qdatetime(attrs['minimum']))
        self.set_max_datetime(as_qdatetime(attrs['maximum']))
        self.set_datetime(as_qdatetime(attrs['datetime']))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_datetime(self, payload):
        """ Handle the 'set-datetime' action from the Enaml widget.
    
        """
        self.set_datetime(as_qdatetime(payload['datetime']))

    def on_message_set_minimum(self, payload):
        """ Hanlde the 'set-minimum' action from the Enaml widget.

        """
        self.set_min_datetime(as_qdatetime(payload['minimum']))

    def on_message_set_maximum(self, payload):
        """ Handle the 'set-maximum' action from the Enaml widget.

        """
        self.set_max_datetime(as_qdatetime(payload['maximum']))

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_date_changed(self):
        """ A signal handler to connect to the datetime changed signal 
        of the underlying widget.

        This will convert the QDateTime to iso format and send the Enaml
        widget the 'event-changed' action.

        """
        qdatetime = self.get_datetime()
        payload = {
            'action': 'event-changed', 'datetime': as_iso_datetime(qdatetime),
        }
        self.send_message(payload)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def get_datetime(self):
        """ Return the current datetime in the control as a QDateTime
        object.

        """
        raise NotImplementedError

    def set_datetime(self, datetime):
        """ Set the widget's datetime

        """
        raise NotImplementedError

    def set_max_datetime(self, datetime):
        """ Set the widget's maximum datetime

        """
        raise NotImplementedError

    def set_min_datetime(self, datetime):
        """ Set the widget's minimum datetime

        """
        raise NotImplementedError

