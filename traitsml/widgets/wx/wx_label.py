import wx

from traits.api import implements, Str

from .wx_element import WXElement

from ..i_label import ILabel


class WXLabel(WXElement):
    """ A wxPython implementation of ILabel.

    A WXLabel displays static text using a wx.StaticText control.

    See Also
    --------
    ILabel

    """
    implements(ILabel)

 	#===========================================================================
    # ILabel interface 
    #===========================================================================
    text = Str

    #===========================================================================
    # Implementation
    #===========================================================================

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying text control.

        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        self.widget = wx.StaticText(self.parent_widget())

    def init_attributes(self):
        """ Initializes the attributes on the underlying control.

        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        self.set_label(self.text)

    def init_meta_handlers(self):
        """ Intializes the meta handlers for the underlying control.

        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        pass

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _text_changed(self, text):
        """ The change handler for the 'text' attribute. Not meant for
        public consumption.

        """
        self.set_label(text)

    #---------------------------------------------------------------------------
    # Widget update
    #---------------------------------------------------------------------------
    def set_label(self, label):
        """ Sets the label on the underlying control. Not meant for
        public consumption.

        """
        self.widget.SetLabel(label)
    
    #---------------------------------------------------------------------------
    # Layout helpers
    #---------------------------------------------------------------------------
    def default_sizer_flags(self):
        """ Updates the default sizer flags to have a proportion of 1.

        """
        # Labels need to claim a bit of space (rather than just be fixed)
        # so that groups of labels arrange cleanly.
        return super(WXLabel, self).default_sizer_flags().Proportion(1)

