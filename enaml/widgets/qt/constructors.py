from traits.api import implements

from ...constructors import IToolkitConstructor, BaseToolkitCtor


#-------------------------------------------------------------------------------
# Constructor helper mixins
#-------------------------------------------------------------------------------
class WrapWindowMixin(object):
    """ A mixin that wraps a constructor in a WXWindowCtor

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

'''
class WXDialogCtor(WXBaseWindowCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..dialog import Dialog
        from .wx_dialog import WXDialog
        dialog = Dialog(toolkit_impl=WXDialog())
        return dialog
'''

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

'''
#-------------------------------------------------------------------------------
# Container Constructors
#-------------------------------------------------------------------------------
class WXFormCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..form import Form
        from .wx_form import WXForm
        form = Form(_impl=WXForm())
        return form
'''

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

'''
class WXStackedGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..stacked_group import StackedGroup
        from .wx_stacked_group import WXStackedGroup
        stacked_group = StackedGroup(toolkit_impl=WXStackedGroup())
        return stacked_group


class WXTabGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..tab_group import TabGroup
        from .wx_tab_group import WXTabGroup
        tab_group = TabGroup(toolkit_impl=WXTabGroup())
        return tab_group


#-------------------------------------------------------------------------------
# Element Constructors
#-------------------------------------------------------------------------------
class WXGroupBoxCtor(WXBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..group_box import GroupBox
        from .wx_group_box import WXGroupBox
        group_box = GroupBox(toolkit_impl=WXGroupBox())
        return group_box


class WXCalendarCtor(WXBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..calendar import Calendar
        from .wx_calendar import WXCalendar
        calendar = Calendar(toolkit_impl=WXCalendar())
        return calendar


class WXCheckBoxCtor(WXBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..check_box import CheckBox
        from .wx_check_box import WXCheckBox
        check_box = CheckBox(toolkit_impl=WXCheckBox())
        return check_box


class WXComboBoxCtor(WXBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..combo_box import ComboBox
        from .wx_combo_box import WXComboBox
        combo_box = ComboBox(toolkit_impl=WXComboBox())
        return combo_box


class WXFieldCtor(WXBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..field import Field
        from .wx_field import WXField
        field = Field(toolkit_impl=WXField())
        return field


class WXHtmlCtor(WXBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..html import Html
        from .wx_html import WXHtml
        html = Html(toolkit_impl=WXHtml())
        return html


class WXImageCtor(WXBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..image import Image
        from .wx_image import WXImage
        image = Image(toolkit_impl=WXImage())
        return image
'''

class QtLabelCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..label import Label
        from .qt_label import QtLabel
        label = Label(toolkit_impl=QtLabel())
        return label


class QtLineEditCtor(QtBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..line_edit import LineEdit
        from .qt_line_edit import QtLineEdit
        line_edit = LineEdit(toolkit_impl=QtLineEdit())
        return line_edit

'''
class WXPushButtonCtor(WXBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..push_button import PushButton
        from .wx_push_button import WXPushButton
        push_button = PushButton(toolkit_impl=WXPushButton())
        return push_button


class WXRadioButtonCtor(WXBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..radio_button import RadioButton
        from .wx_radio_button import WXRadioButton
        radio_button = RadioButton(toolkit_impl=WXRadioButton())
        return radio_button


class WXSliderCtor(WXBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..slider import Slider
        from .wx_slider import WXSlider
        slider = Slider(toolkit_impl=WXSlider())
        return slider


class WXSpinBoxCtor(WXBaseComponentCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..spin_box import SpinBox
        from .wx_spin_box import WXSpinBox
        spin_box = SpinBox(toolkit_impl=WXSpinBox())
        return spin_box

'''

class QtTraitsUIItemCtor(QtBaseComponentCtor):
    
    implements(IToolkitConstructor)

    def component(self):
        from ..traitsui_item import TraitsUIItem
        from .qt_traitsui_item import QtTraitsUIItem
        traitsui_item = TraitsUIItem(toolkit_impl=QtTraitsUIItem())
        return traitsui_item
