""" wx-specific utilities.
"""

import wx


def invoke_later(callable, *args, **kwds):
    """ Invoke a function later in the event loop.

    """
    wx.CallAfter(callable, *args, **kwds)

