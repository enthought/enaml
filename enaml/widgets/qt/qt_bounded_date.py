#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_control import QtControl

from ..bounded_date import AbstractTkBoundedDate


class QtBoundedDate(QtControl, AbstractTkBoundedDate):
    """ A base class for use with widgets implementing behavior
    for subclasses of BoundedDate.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def initialize(self):
        super(QtBoundedDate, self).initialize()
        shell = self.shell_obj
        self.set_min_date(shell.min_date)
        self.set_max_date(shell.max_date)
        self.set_date(shell.date)

    #--------------------------------------------------------------------------
    # Abstract implementation methods
    #--------------------------------------------------------------------------
    def shell_date_changed(self, date):
        self.set_date(date)
    
    def shell_min_date_changed(self, min_date):
        self.set_min_date(min_date)
    
    def shell_max_date_changed(self, max_date):
        self.set_max_date(max_date)

    #--------------------------------------------------------------------------
    # Widget modification methods
    #--------------------------------------------------------------------------
    def set_date(self, date):
        raise NotImplementedError
    
    def set_min_date(self, min_date):
        raise NotImplementedError
    
    def set_max_date(self, max_date):
        raise NotImplementedError

    