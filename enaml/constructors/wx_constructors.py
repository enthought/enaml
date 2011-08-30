from traits.api import implements

from .i_toolkit_constructor import IToolkitConstructor
from .base_constructors import (BasePanelCtor, BaseWindowCtor,
                                BaseContainerCtor, BaseElementCtor)

from ..view import View, NamespaceProxy


#-------------------------------------------------------------------------------
# Base Constructors
#-------------------------------------------------------------------------------
class WXBaseWindowCtor(BaseWindowCtor):

    def build_view(self):
        window = self.impl
        ns = NamespaceProxy(self.global_ns)
        return View(window=window, ns=ns)


class WXBasePanelCtor(BasePanelCtor):

    def build_view(self):
        # This code should never execute because the __call__
        # method makes sure the code path is only taken by a Window.
        msg = "The universe imploded."
        raise Exception(msg)

    def __call__(self, **ctxt_objs):
        # A panel must be wrapped in a window to be viewable.
        window_ctor = WXWindowCtor(
            children=[
                self,
            ],
        )
        return window_ctor(**ctxt_objs)


class WXBaseContainerCtor(BaseContainerCtor):
    
    def construct(self):
        # Replace any toplevel windows with their internal panel.
        # This facilitates composing other toplevel windows into 
        # another window.
        children = self.children
        for idx, child in enumerate(children):
            if isinstance(child, WXBaseWindowCtor):
                window_children = child.children
                if not window_children:
                    children[idx] = WXPanelCtor()
                else:
                    if len(children) > 1:
                        raise ValueError('A window can only have 1 child.')
                    children[idx] = window_children[0]
        super(WXBaseContainerCtor, self).construct()


    def build_view(self):
        # This code should never execute because the __call__
        # method makes sure the code path is only taken by a Window.
        msg = "The universe imploded."
        raise Exception(msg)

    def __call__(self, **ctxt_objs):
        # A container must be wrapped in a window to be viewable.
        window_ctor = WXWindowCtor(
            children=[
                WXPanelCtor(
                    children=[
                        self,
                    ],
                ),
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
        # An element must be wrapped in a window to be viewable.
        window_ctor = WXWindowCtor(
            children=[
                WXPanelCtor(
                    children=[
                        WXVGroupCtor(
                            children=[
                                self,
                            ],
                        ),
                    ],
                ),
            ],
        )
        return window_ctor(**ctxt_objs)


#-------------------------------------------------------------------------------
# Window constructors
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
# Panel Constructors
#-------------------------------------------------------------------------------
class WXPanelCtor(WXBasePanelCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_panel import WXPanel
        return WXPanel


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


class WXHtmlCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_html import WXHtml
        return WXHtml


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

class WXTraitsUIItemCtor(WXBaseElementCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_traitsui_item import WXTraitsUIItem
        return WXTraitsUIItem




#-------------------------------------------------------------------------------
# Meta Info Constructors
#-------------------------------------------------------------------------------



