import wx

from ...enums import Buttons


BUTTON_MAP = {Buttons.OK: wx.OK,
              Buttons.OK_CANCEL: wx.OK | wx.CANCEL,
              Buttons.YES_NO: wx.YES_NO}
              

def _show_dialog(icon, text='', buttons=Buttons.OK, title='Message'):
    choices = BUTTON_MAP[buttons]
    dialog = wx.MessageDialog(None, text, title, style=icon | choices)
    dialog.ShowModal()

def error(*args, **kwargs):
    icon = wx.ICON_ERROR
    _show_dialog(icon, *args, **kwargs)

def warning(*args, **kwargs):
    icon = wx.ICON_EXCLAMATION
    _show_dialog(icon, *args, **kwargs)
    
def question(*args, **kwargs):
    icon = wx.ICON_QUESTION
    _show_dialog(icon, *args, **kwargs)

def information(*args, **kwargs):
    icon = wx.ICON_INFORMATION
    _show_dialog(icon, *args, **kwargs)
