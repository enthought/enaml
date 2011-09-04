from traits.api import implements

from .i_toolkit_constructor import IToolkitConstructor
from .base_constructors import BaseToolkitCtor

from ..view import View, NamespaceProxy


#-------------------------------------------------------------------------------
# Constructor helper mixins
#-------------------------------------------------------------------------------
class WrapWindowMixin(object):
    """ A mixin that wraps a constructor in a WXWindowCtor

    """
    def build_view(self):
        # This code should never execute because the __call__
        # method makes sure the code path is only taken by a Window.
        msg = "The universe imploded."
        raise Exception(msg)

    def __call__(self, **ctxt_objs):
        # A container is not directly viewable, 
        # it must first be wrapped in a window.
        window_ctor = WXWindowCtor(
            children=[
                self,
            ],
        )
        return window_ctor(**ctxt_objs)


class WrapWindowVGroupMixin(WrapWindowMixin):
    """ A mixin that wraps a constructor in a WXWindowCtor with
    a WXVGroupCtor as its container.

    """
    def __call__(self, **ctxt_objs):
        # An element is not directly viewable, it must 
        # first be wrapped in a window and container.
        window_ctor = WXWindowCtor(
            children=[
                WXVGroupCtor(
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
class WXBasePanelCtor(BaseToolkitCtor, WrapWindowVGroupMixin):
    pass


class WXBaseContainerCtor(BaseToolkitCtor, WrapWindowMixin):
    
    def construct(self):
        # Replace any toplevel windows with panel constructors.
        # This facilitates composing other toplevel windows into 
        # another window. Also, the IPanel interface has no 
        # attributes, so we don't need (or want) to copy over
        # the exprs from then window constuctor, just the metas
        # and the children.
        children = self.children
        for idx, child in enumerate(children):
            if isinstance(child, WXBaseWindowCtor):
                window_children = child.children
                window_metas = child.metas
                children[idx] = WXPanelCtor(children=window_children,
                                            metas=window_metas)
        super(WXBaseContainerCtor, self).construct()


class WXBaseElementCtor(BaseToolkitCtor, WrapWindowVGroupMixin):
    pass


class WXBaseWindowCtor(BaseToolkitCtor):

    def build_view(self):
        window = self.impl
        ns = NamespaceProxy(self.global_ns)
        return View(window=window, ns=ns)


#-------------------------------------------------------------------------------
# Window constructors
#-------------------------------------------------------------------------------
class WXWindowCtor(WXBaseWindowCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.window import Window
        from ..widgets.wx.wx_window import WXWindow
        window = Window(toolkit_impl=WXWindow())
        return window


class WXDialogCtor(WXBaseWindowCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.dialog import Dialog
        from ..widgets.wx.wx_dialog import WXDialog
        dialog = Dialog(toolkit_impl=WXDialog())
        return dialog


#-------------------------------------------------------------------------------
# Panel Constructors
#-------------------------------------------------------------------------------
class WXPanelCtor(WXBasePanelCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.panel import Panel
        from ..widgets.wx.wx_panel import WXPanel
        panel = Panel(toolkit_impl=WXPanel())
        return panel


#-------------------------------------------------------------------------------
# Container Constructors
#-------------------------------------------------------------------------------
class WXFormCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.form import Form
        from ..widgets.wx.wx_form import WXForm
        form = Form(_impl=WXForm())
        return form


class WXGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.group import Group
        from ..widgets.wx.wx_group import WXGroup
        group = Group(toolkit_impl=WXGroup())
        return group


class WXVGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.vgroup import VGroup
        from ..widgets.wx.wx_vgroup import WXVGroup
        vgroup = VGroup(toolkit_impl=WXVGroup())
        return vgroup


class WXHGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.hgroup import HGroup
        from ..widgets.wx.wx_hgroup import WXHGroup
        hgroup = HGroup(toolkit_impl=WXHGroup())
        return hgroup


class WXStackedGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.stacked_group import StackedGroup
        from ..widgets.wx.wx_stacked_group import WXStackedGroup
        stacked_group = StackedGroup(toolkit_impl=WXStackedGroup())
        return stacked_group


class WXTabGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.tab_group import TabGroup
        from ..widgets.wx.wx_tab_group import WXTabGroup
        tab_group = TabGroup(toolkit_impl=WXTabGroup())
        return tab_group


#-------------------------------------------------------------------------------
# Element Constructors
#-------------------------------------------------------------------------------
class WXGroupBoxCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.group_box import GroupBox
        from ..widgets.wx.wx_group_box import WXGroupBox
        group_box = GroupBox(toolkit_impl=WXGroupBox())
        return group_box


class WXCalendarCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.calendar import Calender
        from ..widgets.wx.wx_calendar import WXCalendar
        calendar = Calendar(toolkit_impl=WXCalendar())
        return calendar


class WXCheckBoxCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.check_box import CheckBox
        from ..widgets.wx.wx_check_box import WXCheckBox
        check_box = CheckBox(toolkit_impl=WXCheckBox())
        return check_box


class WXComboBoxCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.combo_box import ComboBox
        from ..widgets.wx.wx_combo_box import WXComboBox
        combo_box = ComboBox(toolkit_impl=WXComboBox())
        return combo_box


class WXFieldCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.field import Field
        from ..widgets.wx.wx_field import WXField
        field = Field(toolkit_impl=WXField())
        return field


class WXHtmlCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.html import Html
        from ..widgets.wx.wx_html import WXHtml
        html = Html(toolkit_impl=WXHtml())
        return html


class WXImageCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.image import Image
        from ..widgets.wx.wx_image import WXImage
        image = Image(toolkit_impl=WXImage())
        return image


class WXLabelCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.label import Label
        from ..widgets.wx.wx_label import WXLabel
        label = Label(toolkit_impl=WXLabel())
        return label


class WXLineEditCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.line_edit import LineEdit
        from ..widgets.wx.wx_line_edit import WXLineEdit
        line_edit = LineEdit(toolkit_impl=WXLineEdit())
        return line_edit


class WXPushButtonCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.push_button import PushButton
        from ..widgets.wx.wx_push_button import WXPushButton
        push_button = PushButton(toolkit_impl=WXPushButton())
        return push_button


class WXRadioButtonCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.radio_button import RadioButton
        from ..widgets.wx.wx_radio_button import WXRadioButton
        radio_button = RadioButton(toolkit_impl=WXRadioButton())
        return radio_button


class WXSliderCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.slider import Slider
        from ..widgets.wx.wx_slider import WXSlider
        slider = Slider(toolkit_impl=WXSlider())
        return slider

class WXSpinBoxCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.spin_box import SpinBox
        from ..widgets.wx.wx_spin_box import WXSpinBox
        spin_box = SpinBox(toolkit_impl=WXSpinBox())
        return spin_box


#-------------------------------------------------------------------------------
# Meta Info Constructors
#-------------------------------------------------------------------------------



