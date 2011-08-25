from traits.api import implements

from .i_toolkit_constructor import IToolkitConstructor
from .base_constructors import (BaseWindowCtor, BaseContainerCtor, 
                                BaseElementCtor)

from ..view import View, NamespaceProxy


#-------------------------------------------------------------------------------
# Base Constructors
#-------------------------------------------------------------------------------
class WXBaseWindowCtor(BaseWindowCtor):

    def build_view(self):
        impl = self.impl
        ns = self.global_ns
        view = View(window=impl, ns=NamespaceProxy(ns))
        return view


class WXBaseContainerCtor(BaseContainerCtor):

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


class WXBaseElementCtor(BaseElementCtor):

    def build_view(self):
        # This code should never execute because the __call__
        # method makes sure the code path is only taken by a Window.
        msg = "The universe imploded."
        raise Exception(msg)

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
# Window Constructors
#-------------------------------------------------------------------------------
class WXWindowCtor(WXBaseWindowCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_window import WXWindow
        return WXWindow


class WXDialogCtor(WXBaseWindowCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_dialog import WXDialog
        return WXDialog


#-------------------------------------------------------------------------------
# Container Constructors
#-------------------------------------------------------------------------------
class WXFormCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_form import WXForm
        return WXForm


class WXGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_group import WXGroup
        return WXGroup


class WXVGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_vgroup import WXVGroup
        return WXVGroup


class WXHGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_hgroup import WXHGroup
        return WXHGroup


class WXStackedGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_stacked_group import WXStackedGroup
        return WXStackedGroup


class WXTabGroupCtor(WXBaseContainerCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_tab_group import WXTabGroup
        return WXTabGroup


#-------------------------------------------------------------------------------
# Element Constructors
#-------------------------------------------------------------------------------
class WXGroupBoxCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_group_box import WXGroupBox
        return WXGroupBox


class WXCalendarCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_calendar import WXCalendar
        return WXCalendar


class WXCheckBoxCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_check_box import WXCheckBox
        return WXCheckBox


class WXComboBoxCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_combo_box import WXComboBox
        return WXComboBox


class WXFieldCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_field import WXField
        return WXField


class WXHTMLCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_html import WXHTML
        return WXHTML


class WXImageCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_image import WXImage
        return WXImage


class WXLabelCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_label import WXLabel
        return WXLabel


class WXLineEditCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_line_edit import WXLineEdit
        return WXLineEdit


class WXPushButtonCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_push_button import WXPushButton
        return WXPushButton


class WXRadioButtonCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_radio_button import WXRadioButton
        return WXRadioButton


class WXSliderCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_slider import WXSlider
        return WXSlider


class WXSpinBoxCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_spin_box import WXSpinBox
        return WXSpinBox


#-------------------------------------------------------------------------------
# Meta Info Constructors
#-------------------------------------------------------------------------------



