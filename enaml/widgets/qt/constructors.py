from traits.api import implements

from ...constructors import IToolkitConstructor, BaseToolkitCtor


#-------------------------------------------------------------------------------
# Constructor helper mixins
#-------------------------------------------------------------------------------
class WrapWindowMixin(object):
    """ A mixin that wraps a constructor in a QtWindowCtor

    """
    def __call__(self, **ctxt_objs):
        # A container is not directly viewable, 
        # it must first be wrapped in a window.
        window_ctor = QtWindowCtor(
            children=[
                self,
            ],
        )
        return window_ctor(**ctxt_objs)


class WrapWindowVGroupMixin(WrapWindowMixin):
    """ A mixin that wraps a constructor in a QtWindowCtor with
    a QtVGroupCtor as its container.

    """
    def __call__(self, **ctxt_objs):
        # An element is not directly viewable, it must 
        # first be wrapped in a window and container.
        window_ctor = QtWindowCtor(
            children=[
                QtVGroupCtor(
                    children=[
                        self,
                    ],
                ),
            ],
        )
        return window_ctor(**ctxt_objs)


#-------------------------------------------------------------------------------
# Base Constructors
#-------------------------------------------------------------------------------
class QtBaseWindowCtor(BaseToolkitCtor):
    pass


class QtBasePanelCtor(BaseToolkitCtor, WrapWindowVGroupMixin):
    pass


class QtBaseContainerCtor(BaseToolkitCtor, WrapWindowMixin):
    
    def construct(self):
        # Replace any toplevel windows with panel constructors.
        # This facilitates composing other toplevel windows into 
        # another window. Also, the IPanel interface has no 
        # attributes, so we don't need (or want) to copy over
        # the exprs from then window constuctor, just the metas
        # and the children.
        children = self.children
        for idx, child in enumerate(children):
            if isinstance(child, QtBaseWindowCtor):
                window_children = child.children
                window_metas = child.metas
                children[idx] = QtPanelCtor(children=window_children,
                                            metas=window_metas)
        super(QtBaseContainerCtor, self).construct()


class QtBaseComponentCtor(BaseToolkitCtor, WrapWindowVGroupMixin):
    pass


#-------------------------------------------------------------------------------
# Window constructors
#-------------------------------------------------------------------------------
class QtWindowCtor(QtBaseWindowCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..window import Window
        from .qt_window import QtWindow
        window = Window(toolkit_impl=QtWindow())
        return window


class QtDialogCtor(QtBaseWindowCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..dialog import Dialog
        from .qt_dialog import QtDialog
        dialog = Dialog(toolkit_impl=QtDialog())
        return dialog


#-------------------------------------------------------------------------------
# Panel Constructors
#-------------------------------------------------------------------------------
class QtPanelCtor(QtBasePanelCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..panel import Panel
        from .qt_panel import QtPanel
        panel = Panel(toolkit_impl=QtPanel())
        return panel


#-------------------------------------------------------------------------------
# Container Constructors
#-------------------------------------------------------------------------------
class QtFormCtor(QtBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..form import Form
        from .qt_form import QtForm
        form = Form(_impl=QtForm())
        return form


class QtGroupCtor(QtBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..group import Group
        from .qt_group import QtGroup
        group = Group(toolkit_impl=QtGroup())
        return group


class QtVGroupCtor(QtBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..vgroup import VGroup
        from .qt_vgroup import QtVGroup
        vgroup = VGroup(toolkit_impl=QtVGroup())
        return vgroup


class QtHGroupCtor(QtBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..hgroup import HGroup
        from .qt_hgroup import QtHGroup
        hgroup = HGroup(toolkit_impl=QtHGroup())
        return hgroup


class QtStackedGroupCtor(QtBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..stacked_group import StackedGroup
        from .qt_stacked_group import QtStackedGroup
        stacked_group = StackedGroup(toolkit_impl=QtStackedGroup())
        return stacked_group


class QtTabGroupCtor(QtBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..tab_group import TabGroup
        from .qt_tab_group import QtTabGroup
        tab_group = TabGroup(toolkit_impl=QtTabGroup())
        return tab_group


#-------------------------------------------------------------------------------
# Element Constructors
#-------------------------------------------------------------------------------
class QtGroupBoxCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..group_box import GroupBox
        from .qt_group_box import QtGroupBox
        group_box = GroupBox(toolkit_impl=QtGroupBox())
        return group_box


class QtCalendarCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..calendar import Calendar
        from .qt_calendar import QtCalendar
        calendar = Calendar(toolkit_impl=QtCalendar())
        return calendar


class QtCheckBoxCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..check_box import CheckBox
        from .qt_check_box import QtCheckBox
        check_box = CheckBox(toolkit_impl=QtCheckBox())
        return check_box


class QtComboBoxCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..combo_box import ComboBox
        from .qt_combo_box import QtComboBox
        combo_box = ComboBox(toolkit_impl=QtComboBox())
        return combo_box


class QtFieldCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..field import Field
        from .qt_field import QtField
        field = Field(toolkit_impl=QtField())
        return field


class QtHtmlCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..html import Html
        from .qt_html import QtHtml
        html = Html(toolkit_impl=QtHtml())
        return html


class QtImageCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..image import Image
        from .qt_image import QtImage
        image = Image(toolkit_impl=QtImage())
        return image


class QtLabelCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..label import Label
        from .qt_label import QtLabel
        label = Label(toolkit_impl=QtLabel())
        return label


class QtPushButtonCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..push_button import PushButton
        from .qt_push_button import QtPushButton
        push_button = PushButton(toolkit_impl=QtPushButton())
        return push_button


class QtRadioButtonCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..radio_button import RadioButton
        from .qt_radio_button import QtRadioButton
        radio_button = RadioButton(toolkit_impl=QtRadioButton())
        return radio_button


class QtSliderCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..slider import Slider
        from .qt_slider import QtSlider
        slider = Slider(toolkit_impl=QtSlider())
        return slider


class QtSpinBoxCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..spin_box import SpinBox
        from .qt_spin_box import QtSpinBox
        spin_box = SpinBox(toolkit_impl=QtSpinBox())
        return spin_box
        
        
class QtTraitsUIItemCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..traitsui_item import TraitsUIItem
        from .qt_traitsui_item import QtTraitsUIItem
        traitsui_item = TraitsUIItem(toolkit_impl=QtTraitsUIItem())
        return traitsui_item
        
        
class QtEnableCanvasCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..enable_canvas import EnableCanvas
        from .qt_enable_canvas import QtEnableCanvas
        canvas = EnableCanvas(toolkit_impl=QtEnableCanvas())
        return canvas


class QtTableViewCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..table_view import TableView
        from .qt_table_view import QtTableView
        table_view = TableView(toolkit_impl=QtTableView())
        return table_view


class QtCheckGroupCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..check_group import CheckGroup
        from .qt_check_group import QtCheckGroup
        check_group = CheckGroup(toolkit_impl=QtCheckGroup())
        return check_group
