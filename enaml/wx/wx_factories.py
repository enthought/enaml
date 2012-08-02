#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
def calendar_factory():
    from .wx_calendar import WxCalendar
    return WxCalendar


def check_box_factory():
    from .wx_check_box import WxCheckBox
    return WxCheckBox


def combo_box_factory():
    from .wx_combo_box import WxComboBox
    return WxComboBox


def container_factory():
    from .wx_container import WxContainer
    return WxContainer


def date_selector_factory():
    from .wx_date_selector import WxDateSelector
    return WxDateSelector


# def datetime_selector_factory():
#     from .wx_datetime_selector import WxDatetimeSelector
#     return WxDatetimeSelector


# def dialog_factory():
#     from .wx_dialog import WxDialog
#     return WxDialog


# def field_factory():
#     from .wx_field import WxField
#     return WxField


# def form_factory():
#     from .wx_form import WxForm
#     return WxForm


def group_box_factory():
    from .wx_group_box import WxGroupBox
    return WxGroupBox


def html_factory():
    from .wx_html import WxHtml
    return WxHtml


# def image_view_factory():
#     from .wx_image_view import WxImageView
#     return WxImageView


# def label_factory():
#     from .wx_label import WxLabel
#     return WxLabel


# def notebook_factory():
#     from .wx_notebook import WxNotebook
#     return WxNotebook


# def page_factory():
#     from .wx_page import WxPage
#     return WxPage


def push_button_factory():
    from .wx_push_button import WxPushButton
    return WxPushButton


# def progress_bar_factory():
#     from .wx_progress_bar import WxProgressBar
#     return WxProgressBar


def radio_button_factory():
    from .wx_radio_button import WxRadioButton
    return WxRadioButton


# def scroll_area_factory():
#     from .wx_scroll_area import WxScrollArea
#     return WxScrollArea


def slider_factory():
    from .wx_slider import WxSlider
    return WxSlider


# def spin_box_factory():
#     from .wx_spin_box import WxSpinBox
#     return WxSpinBox


# def splitter_factory():
#     from .wx_splitter import WxSplitter
#     return WxSplitter


# def text_editor_factory():
#     from .wx_text_editor import WxTextEditor
#     return WxTextEditor


def window_factory():
    from .wx_window import WxWindow
    return WxWindow


WX_FACTORIES = {
    'Calendar': calendar_factory,
    'CheckBox': check_box_factory,
    'ComboBox': combo_box_factory,
    'Container': container_factory,
    'DateSelector': date_selector_factory,
    #'DatetimeSelector': datetime_selector_factory,
    #'Dialog': dialog_factory,
    #'Field': field_factory,
    #'Form': form_factory,
    'GroupBox': group_box_factory,
    'Html': html_factory,
    #'ImageView': image_view_factory,
    #'Label': label_factory,
    #'Notebook': notebook_factory,
    #'Page': page_factory,
    'PushButton': push_button_factory,
    #'ProgressBar': progress_bar_factory,
    'RadioButton': radio_button_factory,
    #'ScrollArea': scroll_area_factory,
    'Slider': slider_factory,
    #'SpinBox': spin_box_factory,
    #'Splitter': splitter_factory,
    #'TextEditor': text_editor_factory,
    'Window': window_factory,
}

