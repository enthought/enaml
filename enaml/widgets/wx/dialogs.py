#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ...enums import Buttons


def _show_dialog(icon, text='', buttons=Buttons.OK, title='Message'):
    import wx
    BUTTON_MAP = {Buttons.OK: wx.OK,
                  Buttons.OK_CANCEL: wx.OK | wx.CANCEL,
                  Buttons.YES_NO: wx.YES_NO}
    
    choices = BUTTON_MAP[buttons]
    dialog = wx.MessageDialog(None, text, title, style=icon | choices)
    dialog.ShowModal()

def error(*args, **kwargs):
    from wx import ICON_ERROR
    _show_dialog(ICON_ERROR, *args, **kwargs)

def warning(*args, **kwargs):
    from wx import ICON_EXCLAMATION
    _show_dialog(ICON_EXCLAMATION, *args, **kwargs)
    
def question(*args, **kwargs):
    from wx import ICON_QUESTION
    _show_dialog(ICON_QUESTION, *args, **kwargs)

def information(*args, **kwargs):
    from wx import ICON_INFORMATION
    _show_dialog(ICON_INFORMATION, *args, **kwargs)
