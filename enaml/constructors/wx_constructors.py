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
        window = Window(_impl=WXWindow())
        window._impl.parent = window
        return window


class WXDialogCtor(WXBaseWindowCtor):

    implements(IToolkitConstructor)

    def component(self):
        from ..widgets.dialog import Dialog
        from ..widgets.wx.wx_dialog import WXDialog
        dialog = Dialog(_impl=WXDialog())
        dialog._impl.parent = dialog
        return dialog


#-------------------------------------------------------------------------------
# Panel Constructors
#-------------------------------------------------------------------------------
class WXPanelCtor(WXBasePanelCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.panel import Panel
        from ..widgets.wx.wx_panel import WXPanel
        panel = Panel(_impl=WXPanel())
        panel._impl.parent = panel
        return panel


#-------------------------------------------------------------------------------
# Container Constructors
#-------------------------------------------------------------------------------
class WXFormCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.form import Form
        from ..widgets.wx.wx_form import WXForm
        form = Form(_impl=WXForm())
        form._impl.parent = form
        return form


class WXGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.group import Group
        from ..widgets.wx.wx_group import WXGroup
        group = Group(_impl=WXGroup())
        group._impl.parent = group
        return group


class WXVGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.vgroup import VGroup
        from ..widgets.wx.wx_vgroup import WXVGroup
        vgroup = VGroup(_impl=WXVGroup())
        vgroup._impl.parent = vgroup
        return vgroup


class WXHGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.hgroup import HGroup
        from ..widgets.wx.wx_hgroup import WXHGroup
        hgroup = HGroup(_impl=WXHGroup())
        hgroup._impl.parent = hgroup
        return hgroup


class WXStackedGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.stacked_group import StackedGroup
        from ..widgets.wx.wx_stacked_group import WXStackedGroup
        stacked_group = StackedGroup(_impl=WXStackedGroup())
        stacked_group._impl.parent = stacked_group
        return stacked_group


class WXTabGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.tab_group import TabGroup
        from ..widgets.wx.wx_tab_group import WXTabGroup
        tab_group = TabGroup(_impl=WXTabGroup())
        tab_group._impl.parent = tab_group
        return tab_group


#-------------------------------------------------------------------------------
# Element Constructors
#-------------------------------------------------------------------------------
class WXGroupBoxCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.group_box import GroupBox
        from ..widgets.wx.wx_group_box import WXGroupBox
        group_box = GroupBox(_impl=WXGroupBox())
        group_box._impl.parent = group_box
        return group_box


class WXCalendarCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.calendar import Calender
        from ..widgets.wx.wx_calendar import WXCalendar
        calendar = Calendar(_impl=WXCalendar())
        calendar._impl.parent = calendar
        return calendar


class WXCheckBoxCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.check_box import CheckBox
        from ..widgets.wx.wx_check_box import WXCheckBox
        check_box = CheckBox(_impl=WXCheckBox())
        check_box._impl.parent = check_box
        return check_box


class WXComboBoxCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.combo_box import ComboBox
        from ..widgets.wx.wx_combo_box import WXComboBox
        combo_box = ComboBox(_impl=WXComboBox())
        combo_box._impl.parent = combo_box
        return combo_box


class WXFieldCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.field import Field
        from ..widgets.wx.wx_field import WXField
        field = Field(_impl=WXField())
        field._impl.parent = field
        return field


class WXHtmlCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.html import Html
        from ..widgets.wx.wx_html import WXHtml
        html = Html(_impl=WXHtml())
        html._impl.parent = html
        return html


class WXImageCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.image import Image
        from ..widgets.wx.wx_image import WXImage
        image = Image(_impl=WXImage())
        image._impl.parent = image
        return image


class WXLabelCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.label import Label
        from ..widgets.wx.wx_label import WXLabel
        label = Label(_impl=WXLabel())
        label._impl.parent = label
        return label


class WXLineEditCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.line_edit import LineEdit
        from ..widgets.wx.wx_line_edit import WXLineEdit
        line_edit = LineEdit(_impl=WXLineEdit())
        line_edit._impl.parent = line_edit
        return line_edit


class WXPushButtonCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.push_button import PushButton
        from ..widgets.wx.wx_push_button import WXPushButton
        push_button = PushButton(_impl=WXPushButton())
        push_button._impl.parent = push_button
        return push_button


class WXRadioButtonCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.radio_button import RadioButton
        from ..widgets.wx.wx_radio_button import WXRadioButton
        radio_button = RadioButton(_impl=WXRadioButton())
        radio_button._impl.parent = radio_button
        return radio_button


class WXSliderCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.slider import Slider
        from ..widgets.wx.wx_slider import WXSlider
        slider = Slider(_impl=WXSlider())
        slider._impl.parent = slider


class WXSpinBoxCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.spin_box import SpinBox
        from ..widgets.wx.wx_spin_box import WXSpinBox
        spin_box = SpinBox(_impl=WXSpinBox())
        spin_box._impl.parent = spin_box
        return spin_box


#-------------------------------------------------------------------------------
# Meta Info Constructors
#-------------------------------------------------------------------------------



