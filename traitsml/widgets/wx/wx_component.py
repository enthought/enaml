import wx

from traits.api import implements, HasStrictTraits, Instance, Str

from ..mixins.meta_info_mixin import MetaInfoMixin

from ..i_component import IComponent


class WXComponent(HasStrictTraits, MetaInfoMixin):

    implements(IComponent)

    #---------------------------------------------------------------------------
    # IComponent interface
    #---------------------------------------------------------------------------
    name = Str

    def toolkit_widget(self):
        return self.widget

    # The rest of the interface comes from MetaInfoMixin

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    widget = Instance(wx.Object)

    