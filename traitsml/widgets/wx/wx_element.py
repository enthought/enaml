from traits.api import implements

from ..i_element import IElement

from .wx_component import WXComponent


class WXElement(WXComponent):

    implements(IElement)

    #===========================================================================
    # IElement interface
    #===========================================================================
    def layout(self, parent):
<<<<<<< wx_local
        self.create_widget(parent)
        self.init_attributes()
        self.init_meta_handlers()

    #===========================================================================
    # Implementation
    #===========================================================================
    def create_widget(self, parent):
        raise NotImplementedError
        
    def init_attributes(self):
        raise NotImplementedError

    def init_meta_handlers(self):
        raise NotImplementedError

=======
        self.set_parent(parent)
        self.create_widget()
        self.init_attributes()
        self.init_meta_handlers()

    #===========================================================================
    # Implementation
    #===========================================================================

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self):
        raise NotImplementedError
        
    def init_attributes(self):
        raise NotImplementedError

    def init_meta_handlers(self):
        raise NotImplementedError

     
>>>>>>> local
