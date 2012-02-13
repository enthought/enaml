#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_control import WXControl

from ..bounded_datetime import AbstractTkBoundedDatetime


class WXBoundedDatetime(WXControl, AbstractTkBoundedDatetime):
    """ A base class for use with widgets implementing behavior
    for subclasses of BoundedDatetime.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def initialize(self):
        super(WXBoundedDatetime, self).initialize()
        shell = self.shell_obj
        self.set_min_datetime(shell.min_datetime)
        self.set_max_datetime(shell.max_datetime)
        self.set_datetime(shell.datetime)

    #--------------------------------------------------------------------------
    # Abstract implementation methods
    #--------------------------------------------------------------------------
    def shell_datetime_changed(self, datetime):
        self.set_datetime(datetime)

    def shell_min_datetime_changed(self, min_datetime):
        self.set_min_datetime(min_datetime)

    def shell_max_datetime_changed(self, max_datetime):
        self.set_max_datetime(max_datetime)

    #--------------------------------------------------------------------------
    # Widget modification methods
    #--------------------------------------------------------------------------
    def set_datetime(self, datetime):
        raise NotImplementedError

    def set_min_datetime(self, min_datetime):
        raise NotImplementedError

    def set_max_datetime(self, max_datetime):
        raise NotImplementedError

