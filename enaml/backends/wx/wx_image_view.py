#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_control import WXControl

from ...components.image_view import AbstractTkImageView


class wxBitmapWidget(wx.Panel):
    """ A wx.Panel subclass which paints a provided wx.Bitmap. 

    This differs from wx.StaticBitmap in that it provides the option to
    scale the provided bitmap to the bounds of the widget. If the widget
    is set to scale its contents, low quality scaling will occur during
    resize, with a high quality pass performed once resizing as finished.

    """
    def __init__(self, parent):
        """ Initialize a wxBitmapWidget.

        Parameters
        ----------
        parent : wx.Window
            The wx.Window object which serves as the widget parent.
        
        """
        super(wxBitmapWidget, self).__init__(parent)
        self._bitmap = None
        self._scaled_contents = False
        self._resize_timer = None
        self._resizing = False
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def OnPaint(self, event):
        """ The paint event handler for the widget.

        """
        bmp = self._bitmap
        dc = wx.PaintDC(self)
        if bmp is not None:
            if self._scaled_contents:
                width, height = self.GetSize().asTuple()
                if width != bmp.GetWidth() or height != bmp.GetHeight():
                    img = bmp.ConvertToImage()
                    if self._resizing:
                        quality = wx.IMAGE_QUALITY_NORMAL
                    else:
                        quality = wx.IMAGE_QUALITY_HIGH
                    img.Rescale(width, height, quality)
                    bmp = wx.BitmapFromImage(img)
            dc.DrawBitmap(bmp, 0, 0)

    def OnResize(self, event):
        """ The resize event handler for the widget.

        This method is only bound and called when content scaling is
        enabled. It starts(restarts) a timer to perform a high quality
        scaled repaint when resizing is finished.

        """
        self._resizing = True
        self._resize_timer.Start(60, True)

    def OnResizeEnd(self, event):
        """ The repaint timer event handler.

        This method is only bound and called when content scaling is
        enabled and resizing has completed. It triggers a high quality
        repaint.

        """
        self._resizing = False
        self.Refresh()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetBitmap(self, bitmap):
        """ Get the underlying wx.Bitmap used to paint the control.

        Returns
        -------
        result : wx.Bitmap or None
            The bitmap being used to paint the control, or None if
            no bitmap has been supplied.

        """
        return self._bitmap

    def SetBitmap(self, bitmap):
        """ Set the underlying wx.Bitmap and refresh the widget.

        Parameters
        ----------
        bitmap : wx.Bitmap
            The bitmap to paint on the widget.
        
        """
        self._bitmap = bitmap
        self.Refresh()

    def GetScaledContents(self):
        """ Whether or not the bitmap is scaled to fit the bounds.

        Returns
        -------
        result : bool
            Whether or not the bitmap is scaled to fit the bounds of
            the widget.
        
        """
        return self._scaled_contents
    
    def SetScaledContents(self, scaled):
        """ Set whether or not the bitmap should be scaled to fit the
        bounds of the widget.

        Parameters
        ----------
        scaled : bool
            Whether or not to scale the bitmap to fit the bounds of the
            widget.
        
        """
        if scaled:
            if not self._scaled_contents:
                self._scaled_contents = True
                self._resize_timer = wx.Timer(self)
                self.Bind(wx.EVT_TIMER, self.OnResizeEnd)
                self.Bind(wx.EVT_SIZE, self.OnResize)
        else:
            if self._scaled_contents:
                self._scaled_contents = False
                self._timer = None
                self.Unbind(wx.EVT_TIMER, handler=self.OnResizeEnd)
                self.Unbind(wx.EVT_SIZE, handler=self.OnResize)
        self.Refresh()

    def GetBestSize(self):
        """ Overridden method to return the size of the bitmap as the 
        best size for the widget.

        """
        bmp = self._bitmap
        return wx.Size(bmp.GetWidth(), bmp.GetHeight())

    def GetBestSizeTuple(self):
        """ Overridden method to return the size of the bitmap as the 
        best size for the widget.

        """
        return self.GetBestSize().asTuple()


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
        """ Creates the underlying wxBitmapWidget control.

        """
        self.widget = wxBitmapWidget(parent)

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
        """ Sets the image on the underlying wxBitmapWidget.

        """
        self.widget.SetBitmap(image.as_wxBitmap())

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
    
