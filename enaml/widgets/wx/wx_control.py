import wx

from traits.api import implements

from .wx_component import WXComponent

from ..control import IControlImpl


class WXControl(WXComponent):

    implements(IControlImpl)

    #---------------------------------------------------------------------------
    # IControlImpl interface
    #---------------------------------------------------------------------------
    def layout_child_widgets(self):
        if list(self.child_widgets()):
            raise ValueError('Standard controls cannot have children.')

