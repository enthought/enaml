#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_control import WXControl

from ..bounded_date import AbstractTkBoundedDate


class WXBoundedDate(WXControl, AbstractTkBoundedDate):
    """ A base class for use with widgets implementing behavior
    for subclasses of BoundedDate.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def initialize(self):
        super(WXBoundedDate, self).initialize()
        shell = self.shell_obj
        self._set_min_date(shell.min_date)
        self._set_max_date(shell.max_date)
        self._set_date(shell.date)

    #--------------------------------------------------------------------------
    # Abstract implementation methods
    #--------------------------------------------------------------------------
    def shell_date_changed(self, date):
        self._set_date(date)

    def shell_min_date_changed(self, min_date):
        self._set_min_date(min_date)

    def shell_max_date_changed(self, max_date):
        self._set_max_date(max_date)

    #--------------------------------------------------------------------------
    # Widget modification methods
    #--------------------------------------------------------------------------
    def _set_date(self, date):
        raise NotImplementedError

    def _set_min_date(self, min_date):
        raise NotImplementedError

    def _set_max_date(self, max_date):
        raise NotImplementedError

