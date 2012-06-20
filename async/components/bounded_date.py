#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import date

from traits.api import Date, Property, TraitError, on_trait_change

from .control import Control

from ..core.trait_types import Bounded


class BoundedDate(Control):
    """ A base class for use with widgets that edit a Python 
    datetime.date object bounded between minimum and maximum 
    values. This class is not meant to be used directly.

    """
    #: The minimum date available in the date edit. If not defined then
    #: the default value is September 14, 1752. Extra checks take place 
    #: to make sure that the user does not programmatically set
    #: :attr:`min_date` > :attr:`max_date`.
    min_date = Property(Date, depends_on ='_min_date')

    #: The internal min date storage
    _min_date = Date(date(1752, 9, 14))

    #: The maximum date available in the date edit. If not defined then
    #: the default value is December 31, 7999. Extra checks take place 
    #: to make sure that the user does not programmatically set
    #: :attr:`min_date` > :attr:`max_date`.
    max_date = Property(Date, depends_on ='_max_date')

    #: The internal max date storage
    _max_date = Date(date(7999, 12, 31))

    #: The currently selected date. Default is the current date. The
    #: value is bounded between :attr:`min_date` and :attr:`max_date`. 
    #: Changing the boundary attributes might result in an update of 
    #: :attr:`date` to fit in the new range. Attempts to assign a value 
    #: outside of these bounds will result in a TraitError.
    date = Bounded(Date(date.today()), low='min_date', high='max_date')

    @on_trait_change('date, max_date, min_date')
    def sync_object_state(self, name, new):
        msg = 'set_' + name
        self.send(msg, {'value':new})

    def initial_attrs(self):
        super_attrs = super(BoundedDate, self).inital_attrs()
        attrs = {'date':self.date, 'max_date':self.max_date, 'min_date':self.min_date}
        attrs.update(super_attrs)
        return attrs

    #--------------------------------------------------------------------------
    # Property methods
    #--------------------------------------------------------------------------
    def _set_min_date(self, date):
        """ Set the min_date. Addtional checks are applied to make sure 
        that :attr:`min_date` < :attr:`max_date`

        """
        if date > self.max_date:
            msg = ("The minimum date should be smaller than the current "
                   "maximum date({0}), but a value of {1} was given.")
            msg = msg.format(self.max_date, date)
            raise TraitError(msg)
        self._min_date = date

    def _set_max_date(self, date):
        """ Set the max_date. Addtional checks are applied to make sure
        that :attr:`min_date` < :attr:`max_date`

        """
        if date < self.min_date:
            msg = ("The maximum date should be larger than the current "
                   "minimum date({0}), but a value of {1} was given.")
            msg = msg.format(self.min_date, date)
            raise TraitError(msg)
        self._max_date = date

    def _get_max_date(self):
        """ The property getter for the maximum date.

        """
        return self._max_date

    def _get_min_date(self):
        """ The property getter for the minimum date.

        """
        return self._min_date
    
    @on_trait_change('min_date, max_date')
    def _adapt_date(self):
        """ Adapt the date to the bounderies

        """
        if self.initialized:
            self.date = min(max(self.date, self.min_date), self.max_date)

