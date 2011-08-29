import wx

from traits.api import implements, Instance, Bool

from .wx_component import WXComponent
from .wx_container import WXContainer

from ..i_panel import IPanel


class WXPanel(WXComponent):
    """ A wxPython implementation of IPanel.

    A panel aranges it children onto a wx.Panel.

    See Also
    --------
    IPanel

    """
    implements(IPanel)

    #===========================================================================
    # IPanel interface
    #===========================================================================
    def layout(self, parent):
        """ Layout the children in the panel using the given parent.

        This will not typically be called directly by user code.

        """
        self.set_parent(parent)
        self.create_widget()
        self.layout_container()
        self.init_attributes()
        self.init_meta_handlers()
        self.needs_layout = False

    def set_container(self, container):
        """ Sets the container of child component for this panel.

        """
        self.container = container
        self.needs_container_layout = True

    def get_container(self):
        """ Returns the container of child components.

        """
        return self.container

    #===========================================================================
    # Implementation
    #===========================================================================
    # The container of child widgets
    container = Instance(WXContainer)

    # Whether the window needs to be layed out
    needs_layout = Bool(True)

    # Whether we need to re-layout the container before showing.
    needs_container_layout = Bool(True)

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying wxPanel.

        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        self.widget = wx.Panel(self.parent_widget())

    def layout_container(self):
        """ Lays out the container or child elements. 

        This is called by the 'layout' method and is not meant for
        public consumption.

        """
        container = self.container
        if container is not None:
            for child_widget in self.widget.GetChildren():
                if child_widget:
                    child_widget.Destroy()
            container.layout(self)
            self.widget.SetSizerAndFit(container.widget, True)
        self.needs_container_layout = False

    def init_attributes(self):
        """ Initializes the attributes of the panel.

        This is called by the 'layout' method and is not meant for
        public consumption.

        """
        pass
    
    def init_meta_handlers(self):
        """ Initializes the meta handlers of the panel.

        This is called by the 'layout' method and is not meant for
        public consumption.

        """
        pass

    