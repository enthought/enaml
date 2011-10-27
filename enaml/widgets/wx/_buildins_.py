#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" This module defines extra built-in functions that will be available
from the right-hand side of expressions in .enaml files.

Toolkit-specific modules are imported inside of functions, to avoid
premature imports.
"""

from ...enums import Buttons

def _show_dialog(icon, text='', buttons=Buttons.OK, title=''):
    """ Internal function to display message dialogs (and ignore the result).

    Arguments
    ---------
    icon : int
        The wx icon constant (e.g. wx.ICON_ERROR) to use for the message
        box. The icon defines the type of the message dialog.

    text : str
        The message to display to the user.

    buttons : Buttons
        The buttons options to give to the user

    title : str
        The title of the message box.

    """
    import wx
    BUTTON_MAP = {Buttons.OK: wx.OK,
                  Buttons.OK_CANCEL: wx.OK | wx.CANCEL,
                  Buttons.YES_NO: wx.YES_NO}

    choices = BUTTON_MAP[buttons]

    dialog = wx.MessageDialog(None, text, title, style=icon | choices)
    dialog.ShowModal()

def error(*args, **kwargs):
    """ Show an error message dialog.

    """
    from wx import ICON_ERROR
    _show_dialog(ICON_ERROR, *args, **kwargs)

def warning(*args, **kwargs):
    """ Show a warning message dialog.

    """
    from wx import ICON_EXCLAMATION
    _show_dialog(ICON_EXCLAMATION, *args, **kwargs)

def question(*args, **kwargs):
    """ Show a question message dialog.

    """
    from wx import ICON_QUESTION
    _show_dialog(ICON_QUESTION, *args, **kwargs)

def information(*args, **kwargs):
    """ Show an information message dialog.

    """
    from wx import ICON_INFORMATION
    _show_dialog(ICON_INFORMATION, *args, **kwargs)
