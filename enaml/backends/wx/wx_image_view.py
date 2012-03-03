#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_control import WXControl

from ...components.image_view import AbstractTkImageView


class wxImageWidget(wx.Panel):

    def __init__(self, parent):
        super(wxImageWidget, self).__init__(parent)
        self._bitmap = None
        self._scaled_contents = False
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def GetBitmap(self, bitmap):
        return self._bitmap

    def SetBitmap(self, bitmap):
        self._bitmap = bitmap
        self.Refresh()

    def GetScaledContents(self):
        return self._scaled_contents
    
    def SetScaledContents(self, scaled):
        self._scaled_contents = scaled

    def GetBestSize(self):
        bmp = self._bitmap
        return wx.Size(bmp.GetWidth(), bmp.GetHeight())

    def GetBestSizeTuple(self):
        return self.GetBestSize().asTuple()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        bmp = self._bitmap
        if bmp is not None:
            dc.DrawBitmap(bmp, 0, 0)


class WXImageView(WXControl, AbstractTkImageView):
    """ A Wx implementation of ImageView.

    """
    #: The internal cached size hint which is used to determine whether
    #: of not a size hint updated event should be emitted when the text
    #: in the label changes
    _cached_size_hint = None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.StaticBitmap control.

        """
        self.widget = wxImageWidget(parent)

    def initialize(self):
        """ Initializes the attributes on the underlying control.

        """
        super(WXImageView, self).initialize()
        shell = self.shell_obj
        self.set_image(shell.image)
        self.set_scale_to_fit(shell.scale_to_fit)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_image_changed(self, image):
        """ The change handler for the 'image' attribute on the shell 
        component.

        """
        self.set_image(image)
    
    def shell_scale_to_fit_changed(self, scale_to_fit):
        """ The change handler for the 'scale_to_fit' attribute on the 
        shell component.

        """
        self.set_scale_to_fit(scale_to_fit)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_image(self, image):
        """ Sets the image on the underlying control.

        """
        wxbitmap = image.as_wxBitmap()
        self.widget.SetBitmap(wxbitmap)

        # Emit a size hint updated event if the size hint has actually
        # changed. This is an optimization so that a constraints update
        # only occurs when the size hint has actually changed. This 
        # logic must be implemented here so that the label has been
        # updated before the new size hint is computed. Placing this
        # logic on the shell object would not guarantee that the label
        # has been updated at the time the change handler is called.
        cached = self._cached_size_hint
        hint = self._cached_size_hint = self.size_hint()
        if cached != hint:
            self.shell_obj.size_hint_updated()
    
    def set_scale_to_fit(self, scale_to_fit):        
        """ Sets whether or not the image scales with the underlying 
        control.

        """
        self.widget.SetScaledContents(scale_to_fit)
        # See the comment in set_image(...) about the size hint update
        # notification. The same logic applies here.
        cached = self._cached_size_hint
        hint = self._cached_size_hint = self.size_hint()
        if cached != hint:
            self.shell_obj.size_hint_updated()
    
