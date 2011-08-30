from traits.api import implements

from .i_toolkit_constructor import IToolkitConstructor
from .base_constructors import (BasePanelCtor, BaseContainerCtor, 
                                BaseElementCtor)

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
class WXBasePanelCtor(BasePanelCtor, WrapWindowVGroupMixin):
    pass


class WXBaseContainerCtor(BaseContainerCtor, WrapWindowMixin):
    
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


class WXBaseElementCtor(BaseElementCtor, WrapWindowVGroupMixin):
    pass


class WXBaseWindowCtor(BasePanelCtor):

    def build_view(self):
        window = self.impl
        ns = NamespaceProxy(self.global_ns)
        return View(window=window, ns=ns)


#-------------------------------------------------------------------------------
# Panel Constructors
#-------------------------------------------------------------------------------
class WXPanelCtor(WXBasePanelCtor):

    implements(IToolkitConstructor)

    def toolkit_class(self):
        from ..widgets.wx.wx_panel import WXPanel
        return WXPanel


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



