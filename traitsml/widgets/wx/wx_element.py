from traits.api import implements

from ..i_element import IElement

from .wx_component import WXComponent


class WXElement(WXComponent):

    implements(IElement)

    #---------------------------------------------------------------------------
    # IElement Interface
    #---------------------------------------------------------------------------

    # IElement is currently an empty interface

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def layout(self, parent):
        self.create_widget(parent)
        self.init_attributes()
        self.init_meta_handlers()

