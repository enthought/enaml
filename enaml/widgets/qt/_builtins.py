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


def _show_dialog(dialog_ctor, text='', buttons=Buttons.OK, title=''):
    """ Internal function to display message dialogs (and ignore the result).
    
    """
    from .qt import QtGui
    
    if buttons == Buttons.OK_CANCEL:
        choices = QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel
    elif buttons == Buttons.YES_NO:
        choices = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
    else:
        choices = QtGui.QMessageBox.Ok
    
    dialog_ctor(None, title, text, buttons=choices)
    
def error(*args, **kwargs):
    """ Show an error message dialog.
    
    """
    from .qt import QtGui
    _show_dialog(QtGui.QMessageBox.critical, *args, **kwargs)

def warning(*args, **kwargs):
    """ Show a warning message dialog.
    
    """
    from .qt import QtGui
    _show_dialog(QtGui.QMessageBox.warning, *args, **kwargs)
    
def question(*args, **kwargs):
    """ Show a question message dialog.
    
    """
    from .qt import QtGui
    _show_dialog(QtGui.QMessageBox.question, *args, **kwargs)

def information(*args, **kwargs):
    """ Show an information message dialog.
    
    """
    from .qt import QtGui
    _show_dialog(QtGui.QMessageBox.information, *args, **kwargs)
