#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_bounded_date import WxBoundedDate


class WxDateSelector(WxBoundedDate):
    """ A Wx implementation of an Enaml DateSelector.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying wx.DatePickerCtrl.

        """
        self.widget = wx.DatePickerCtrl(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget's attributes.

        """
        super(WxDateSelector, self).initialize(attrs)
        self.set_date_format(attrs['date_format'])
        self.widget.Bind(wx.EVT_DATE_CHANGED, self.on_date_changed)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_date_format(self, content):
        """ Handle the 'set_date_format' action from the Enaml widget.

        """
        self.set_date_format(content['date_format'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def get_date(self):
        """ Return the current date in the control.

        Returns
        -------
        result : wxDateTime
            The current control date as a wxDateTime object.

        """
        return self.widget.GetValue()

    def set_date(self, date):
        """ Set the widget's current date.

        Parameters
        ----------
        date : wxDateTime
            The wxDateTime object to use for setting the date.

        """
        self.widget.SetValue(date)

    def set_max_date(self, date):
        """ Set the widget's maximum date.

        Parameters
        ----------
        date : wxDateTime
            The wxDateTime object to use for setting the maximum date.

        """
        self.widget.SetRange(self.widget.GetLowerLimit(), date)

    def set_min_date(self, date):
        """ Set the widget's minimum date.

        Parameters
        ----------
        date : wxDateTime
            The wxDateTime object to use for setting the minimum date.

        """
        self.widget.SetRange(date, self.widget.GetUpperLimit())

    def set_date_format(self, date_format):
        """ Set the widget's date format.

        Parameters
        ----------
        date_format : str
            A Python time formatting string.
            
        .. note:: Changing the format on wx is not supported.
                  See http://trac.wxwidgets.org/ticket/10988

        """
        pass

