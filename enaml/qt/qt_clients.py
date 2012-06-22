#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
def window_importer():
    from .qt_window import QtWindow
    return QtWindow


def slider_importer():
    from .qt_slider import QtSlider
    return QtSlider


def push_button_importer():
    from .qt_push_button import QtPushButton
    return QtPushButton


CLIENTS = {
    'Window': window_importer,
    'Slider': slider_importer,
    'PushButton': push_button_importer,
}


