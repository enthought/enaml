#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from wx.lib.newevent import NewCommandEvent


#: A custom command event that can be posted to request a layout
#: when a widget's geometry has changed. On Qt, this type of event
#: is posted and handled automatically. This fills that gap.
wxEvtLayoutRequested, EVT_COMMAND_LAYOUT_REQUESTED = NewCommandEvent()

