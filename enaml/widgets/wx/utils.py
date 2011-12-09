#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" wx-specific utilities.

"""
import wx


def invoke_later(callable, *args, **kwds):
    """ Invoke a function later in the event loop.

    """
    wx.CallAfter(callable, *args, **kwds)


def invoke_timer(ms, callable, *args, **kwds):
    """ Invoke a function some milliseconds from now.

    """
    wx.CallLater(ms, callable, *args, **kwds)

