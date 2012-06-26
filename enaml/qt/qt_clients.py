#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
def window_importer():
    from .qt_window import QtWindow
    return QtWindow


def container_importer():
    from .qt_container import QtContainer
    return QtContainer


def slider_importer():
    from .qt_slider import QtSlider
    return QtSlider


def check_box_importer():
    from .qt_check_box import QtCheckBox
    return QtCheckBox


def radio_button_importer():
    from .qt_radio_button import QtRadioButton
    return QtRadioButton


def push_button_importer():
    from .qt_push_button import QtPushButton
    return QtPushButton


CLIENTS = {
    'Window': window_importer,
    'Container': container_importer,
    'Slider': slider_importer,
    'PushButton': push_button_importer,
    'CheckBox': check_box_importer,
    'RadioButton': radio_button_importer,
}


