#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ...constructors import ImportCtor


#-------------------------------------------------------------------------------
# Base Constructors
#-------------------------------------------------------------------------------
class QtBaseComponentCtor(ImportCtor):
    pass

#-------------------------------------------------------------------------------
# Window constructors
#-------------------------------------------------------------------------------
class QtWindowCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.window:Window'
    impl = 'enaml.widgets.qt.qt_window:QtWindow'


class QtDialogCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.dialog:Dialog'
    impl = 'enaml.widgets.qt.qt_dialog:QtDialog'


#-------------------------------------------------------------------------------
# Panel Constructors
#-------------------------------------------------------------------------------
class QtPanelCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.panel:Panel'
    impl = 'enaml.widgets.qt.qt_panel:QtPanel'


#-------------------------------------------------------------------------------
# Container Constructors
#-------------------------------------------------------------------------------
class QtFormCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.form:Form'
    impl = 'enaml.widgets.qt.qt_form:QtForm'


class QtGroupCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.group:Group'
    impl = 'enaml.widgets.qt.qt_group:QtGroup'


class QtVGroupCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.vgroup:VGroup'
    impl = 'enaml.widgets.qt.qt_vgroup:QtVGroup'


class QtHGroupCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.hgroup:HGroup'
    impl = 'enaml.widgets.qt.qt_hgroup:QtHGroup'


class QtStackedGroupCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.stacked_group:StackedGroup'
    impl = 'enaml.widgets.qt.qt_stacked_group:QtStackedGroup'


class QtTabGroupCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.tab_group:TabGroup'
    impl = 'enaml.widgets.qt.qt_tab_group:QtTabGroup'


#-------------------------------------------------------------------------------
# Element Constructors
#-------------------------------------------------------------------------------
class QtGroupBoxCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.group_box:GroupBox'
    impl = 'enaml.widgets.qt.qt_group_box:QtGroupBox'


class QtCalendarCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.calendar:Calendar'
    impl = 'enaml.widgets.qt.qt_calendar:QtCalendar'


class QtCheckBoxCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.check_box:CheckBox'
    impl = 'enaml.widgets.qt.qt_check_box:QtCheckBox'


class QtComboBoxCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.combo_box:ComboBox'
    impl = 'enaml.widgets.qt.qt_combo_box:QtComboBox'


class QtFieldCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.field:Field'
    impl = 'enaml.widgets.qt.qt_field:QtField'


class QtHtmlCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.html:Html'
    impl = 'enaml.widgets.qt.qt_html:QtHtml'


class QtImageCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.image:Image'
    impl = 'enaml.widgets.qt.qt_image:QtImage'


class QtLabelCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.label:Label'
    impl = 'enaml.widgets.qt.qt_label:QtLabel'


class QtPushButtonCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.push_button:PushButton'
    impl = 'enaml.widgets.qt.qt_push_button:QtPushButton'


class QtRadioButtonCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.radio_button:RadioButton'
    impl = 'enaml.widgets.qt.qt_radio_button:QtRadioButton'


class QtSliderCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.slider:Slider'
    impl = 'enaml.widgets.qt.qt_slider:QtSlider'


class QtSpinBoxCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.spin_box:SpinBox'
    impl = 'enaml.widgets.qt.qt_spin_box:QtSpinBox'
        
        
class QtTraitsUIItemCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.traitsui_item:TraitsUIItem'
    impl = 'enaml.widgets.qt.qt_traitsui_item:QtTraitsUIItem'
        
        
class QtEnableCanvasCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.enable_canvas:EnableCanvas'
    impl = 'enaml.widgets.qt.qt_enable_canvas:QtEnableCanvas'


class QtTableViewCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.table_view:TableView'
    impl = 'enaml.widgets.qt.qt_table_view:QtTableView'


class QtCheckGroupCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.check_group:CheckGroup'
    impl = 'enaml.widgets.qt.qt_check_group:QtCheckGroup'


class QtDateEditCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.date_edit:DateEdit'
    impl = 'enaml.widgets.qt.qt_date_edit:QtDateEdit'


class QtDateTimeEditCtor(QtBaseComponentCtor):
    comp = 'enaml.widgets.datetime_edit:DateTimeEdit'
    impl = 'enaml.widgets.qt.qt_datetime_edit:QtDateTimeEdit'

