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


def field_importer():
    from .qt_field import QtField
    return QtField


def label_importer():
    from .qt_label import QtLabel
    return QtLabel


def calendar_importer():
    from .qt_calendar import QtCalendar
    return QtCalendar


def combo_box_importer():
    from .qt_combo_box import QtComboBox
    return QtComboBox


def date_edit_importer():
    from .qt_date_edit import QtDateEdit
    return QtDateEdit


def datetime_edit_importer():
    from .qt_datetime_edit import QtDatetimeEdit
    return QtDatetimeEdit


def dialog_importer():
    from .qt_dialog import QtDialog
    return QtDialog


def file_dialog_importer():
    from .qt_file_dialog import QtFileDialog
    return QtFileDialog


def html_importer():
    from .qt_html import QtHtml
    return QtHtml


def progress_bar_importer():
    from .qt_progress_bar import QtProgressBar
    return QtProgressBar


def spin_box_importer():
    from .qt_spin_box import QtSpinBox
    return QtSpinBox


CLIENTS = {
    'Window': window_importer,
    'Container': container_importer,
    'Slider': slider_importer,
    'PushButton': push_button_importer,
    'CheckBox': check_box_importer,
    'RadioButton': radio_button_importer,
    'Field': field_importer,
    'Label': label_importer,
    'Calendar': calendar_importer,
    'ComboBox': combo_box_importer,
    'DateEdit': date_edit_importer,
    'DatetimeEdit': datetime_edit_importer,
    'Dialog': dialog_importer,
    'FileDialog': file_dialog_importer,
    'Html': html_importer,
    'ProgressBar': progress_bar_importer,
    'SpinBox': spin_box_importer,
}


