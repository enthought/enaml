#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
def action_factory():
    from .qt_action import QtAction
    return QtAction


def action_group_factory():
    from .qt_action_group import QtActionGroup
    return QtActionGroup


def calendar_factory():
    from .qt_calendar import QtCalendar
    return QtCalendar


def check_box_factory():
    from .qt_check_box import QtCheckBox
    return QtCheckBox


def combo_box_factory():
    from .qt_combo_box import QtComboBox
    return QtComboBox


def container_factory():
    from .qt_container import QtContainer
    return QtContainer


def date_selector_factory():
    from .qt_date_selector import QtDateSelector
    return QtDateSelector


def datetime_selector_factory():
    from .qt_datetime_selector import QtDatetimeSelector
    return QtDatetimeSelector


def dialog_factory():
    from .qt_dialog import QtDialog
    return QtDialog


def dock_pane_factory():
    from .qt_dock_pane import QtDockPane
    return QtDockPane


def field_factory():
    from .qt_field import QtField
    return QtField


def form_factory():
    from .qt_form import QtForm
    return QtForm


def group_box_factory():
    from .qt_group_box import QtGroupBox
    return QtGroupBox


def html_factory():
    from .qt_html import QtHtml
    return QtHtml


def image_view_factory():
    from .qt_image_view import QtImageView
    return QtImageView


def label_factory():
    from .qt_label import QtLabel
    return QtLabel


def main_window_factory():
    from .qt_main_window import QtMainWindow
    return QtMainWindow


def menu_factory():
    from .qt_menu import QtMenu
    return QtMenu


def menu_bar_factory():
    from .qt_menu_bar import QtMenuBar
    return QtMenuBar


def notebook_factory():
    from .qt_notebook import QtNotebook
    return QtNotebook


def page_factory():
    from .qt_page import QtPage
    return QtPage


def push_button_factory():
    from .qt_push_button import QtPushButton
    return QtPushButton


def progress_bar_factory():
    from .qt_progress_bar import QtProgressBar
    return QtProgressBar


def radio_button_factory():
    from .qt_radio_button import QtRadioButton
    return QtRadioButton


def scroll_area_factory():
    from .qt_scroll_area import QtScrollArea
    return QtScrollArea


def slider_factory():
    from .qt_slider import QtSlider
    return QtSlider


def spin_box_factory():
    from .qt_spin_box import QtSpinBox
    return QtSpinBox


def splitter_factory():
    from .qt_splitter import QtSplitter
    return QtSplitter


def text_editor_factory():
    from .qt_text_editor import QtTextEditor
    return QtTextEditor


def tool_bar_factory():
    from .qt_tool_bar import QtToolBar
    return QtToolBar


def window_factory():
    from .qt_window import QtWindow
    return QtWindow


QT_FACTORIES = {
    'Action': action_factory,
    'ActionGroup': action_group_factory,
    'Calendar': calendar_factory,
    'CheckBox': check_box_factory,
    'ComboBox': combo_box_factory,
    'Container': container_factory,
    'DateSelector': date_selector_factory,
    'DatetimeSelector': datetime_selector_factory,
    'DockPane': dock_pane_factory,
    'Dialog': dialog_factory,
    'Field': field_factory,
    'Form': form_factory,
    'GroupBox': group_box_factory,
    'Html': html_factory,
    'ImageView': image_view_factory,
    'Label': label_factory,
    'MainWindow': main_window_factory,
    'Menu': menu_factory,
    'MenuBar': menu_bar_factory,
    'Notebook': notebook_factory,
    'Page': page_factory,
    'PushButton': push_button_factory,
    'ProgressBar': progress_bar_factory,
    'RadioButton': radio_button_factory,
    'ScrollArea': scroll_area_factory,
    'Slider': slider_factory,
    'SpinBox': spin_box_factory,
    'Splitter': splitter_factory,
    'TextEditor': text_editor_factory,
    'ToolBar': tool_bar_factory,
    'Window': window_factory,
}

